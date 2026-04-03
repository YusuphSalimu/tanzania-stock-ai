"""
Tanzania Stock Market AI - Backend API
Flask application for stock predictions and market data
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import DSEDataLoader
from utils.preprocessing import StockDataPreprocessor
from models.predict import StockPredictor

app = Flask(__name__)
CORS(app)

# Initialize components
data_loader = DSEDataLoader()
preprocessor = StockDataPreprocessor()
predictor = StockPredictor()

# Global cache for data
data_cache = {}
last_update = None

@app.route('/')
def home():
    """Home page - API documentation"""
    return jsonify({
        'name': 'Tanzania Stock Market AI API',
        'version': '1.0.0',
        'description': 'AI-powered stock price prediction for Dar es Salaam Stock Exchange',
        'endpoints': {
            '/api/stocks': 'List all available stocks',
            '/api/stocks/<symbol>/data': 'Get stock data',
            '/api/stocks/<symbol>/predict': 'Get stock prediction',
            '/api/stocks/<symbol>/report': 'Get full analysis report',
            '/api/market/summary': 'Market summary',
            '/api/market/top-gainers': 'Top gainers',
            '/api/market/top-losers': 'Top losers',
            '/api/models/train': 'Train models (POST)',
            '/api/portfolio/simulate': 'Portfolio simulation (POST)'
        }
    })

@app.route('/api/stocks')
def get_stocks():
    """Get list of all available stocks"""
    try:
        stocks = data_loader.get_stock_list()
        stock_info = data_loader.dse_stocks
        
        stock_list = []
        for symbol in stocks:
            stock_list.append({
                'symbol': symbol,
                'name': stock_info[symbol],
                'sector': get_stock_sector(symbol)
            })
        
        return jsonify({
            'success': True,
            'stocks': stock_list,
            'total': len(stock_list)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stocks/<symbol>/data')
def get_stock_data(symbol):
    """Get historical data for a specific stock"""
    try:
        # Get stock data
        stock_data = data_loader.get_stock_data(symbol)
        
        if stock_data.empty:
            return jsonify({'success': False, 'error': 'Stock not found'}), 404
        
        # Convert to JSON-friendly format
        data = []
        for _, row in stock_data.iterrows():
            data.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': int(row['volume']),
                'change': float(row['change']),
                'change_percent': float(row['change_percent'])
            })
        
        # Calculate basic statistics
        latest_price = float(stock_data['close'].iloc[-1])
        price_change = float(stock_data['change'].iloc[-1])
        price_change_percent = float(stock_data['change_percent'].iloc[-1])
        
        # 52-week high/low
        week_52_high = float(stock_data['high'].max())
        week_52_low = float(stock_data['low'].min())
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'company_name': data_loader.dse_stocks.get(symbol, 'Unknown'),
            'current_price': latest_price,
            'change': price_change,
            'change_percent': price_change_percent,
            'week_52_high': week_52_high,
            'week_52_low': week_52_low,
            'data': data,
            'total_records': len(data)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stocks/<symbol>/predict')
def get_stock_prediction(symbol):
    """Get prediction for a specific stock"""
    try:
        # Load and prepare data
        df = data_loader.load_data()
        data = preprocessor.prepare_data_for_ml(df, symbol)
        
        # Generate prediction report
        report = predictor.generate_full_report(data, symbol)
        
        return jsonify({
            'success': True,
            'prediction': report
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stocks/<symbol>/report')
def get_stock_report(symbol):
    """Get comprehensive analysis report for a stock"""
    try:
        # Load and prepare data
        df = data_loader.load_data()
        data = preprocessor.prepare_data_for_ml(df, symbol)
        
        # Generate full report
        report = predictor.generate_full_report(data, symbol)
        
        # Add additional analysis
        stock_data = data['stock_data']
        
        # Technical indicators summary
        latest_data = stock_data.iloc[-1]
        technical_summary = {
            'rsi': float(latest_data.get('rsi', 0)),
            'macd': float(latest_data.get('macd', 0)),
            'ma_5': float(latest_data.get('ma_5', 0)),
            'ma_20': float(latest_data.get('ma_20', 0)),
            'bb_upper': float(latest_data.get('bb_upper', 0)),
            'bb_lower': float(latest_data.get('bb_lower', 0)),
            'volume_ratio': float(latest_data.get('volume_ratio', 1))
        }
        
        # Price trend analysis
        price_trend = analyze_price_trend(stock_data)
        
        # Add to report
        report['technical_analysis'] = technical_summary
        report['price_trend'] = price_trend
        report['company_info'] = {
            'name': data_loader.dse_stocks.get(symbol, 'Unknown'),
            'sector': get_stock_sector(symbol),
            'listing_date': '2010-01-01',  # Placeholder
            'market_cap': calculate_market_cap(stock_data)
        }
        
        return jsonify({
            'success': True,
            'report': report
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/market/summary')
def get_market_summary():
    """Get overall market summary"""
    try:
        summary = data_loader.get_market_summary()
        df = data_loader.load_data()
        
        # Get latest market data
        latest_date = df['date'].max()
        latest_data = df[df['date'] == latest_date]
        
        # Calculate market indices
        market_change = latest_data['change_percent'].mean()
        market_volume = latest_data['volume'].sum()
        
        # Top performers
        top_gainers = latest_data.nlargest(5, 'change_percent')
        top_losers = latest_data.nsmallest(5, 'change_percent')
        
        return jsonify({
            'success': True,
            'summary': summary,
            'market_change': round(float(market_change), 2),
            'market_volume': int(market_volume),
            'latest_date': latest_date.strftime('%Y-%m-%d'),
            'top_gainers': [
                {
                    'symbol': row['stock_symbol'],
                    'change_percent': float(row['change_percent'])
                }
                for _, row in top_gainers.iterrows()
            ],
            'top_losers': [
                {
                    'symbol': row['stock_symbol'],
                    'change_percent': float(row['change_percent'])
                }
                for _, row in top_losers.iterrows()
            ]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/market/top-gainers')
def get_top_gainers():
    """Get top gaining stocks"""
    try:
        df = data_loader.load_data()
        latest_date = df['date'].max()
        latest_data = df[df['date'] == latest_date]
        
        top_gainers = latest_data.nlargest(10, 'change_percent')
        
        gainers = []
        for _, row in top_gainers.iterrows():
            gainers.append({
                'symbol': row['stock_symbol'],
                'name': data_loader.dse_stocks.get(row['stock_symbol'], 'Unknown'),
                'price': float(row['close']),
                'change': float(row['change']),
                'change_percent': float(row['change_percent']),
                'volume': int(row['volume'])
            })
        
        return jsonify({
            'success': True,
            'gainers': gainers
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/market/top-losers')
def get_top_losers():
    """Get top losing stocks"""
    try:
        df = data_loader.load_data()
        latest_date = df['date'].max()
        latest_data = df[df['date'] == latest_date]
        
        top_losers = latest_data.nsmallest(10, 'change_percent')
        
        losers = []
        for _, row in top_losers.iterrows():
            losers.append({
                'symbol': row['stock_symbol'],
                'name': data_loader.dse_stocks.get(row['stock_symbol'], 'Unknown'),
                'price': float(row['close']),
                'change': float(row['change']),
                'change_percent': float(row['change_percent']),
                'volume': int(row['volume'])
            })
        
        return jsonify({
            'success': True,
            'losers': losers
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/models/train', methods=['POST'])
def train_models():
    """Train ML models for specific stock or all stocks"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'ALL')
        
        from models.train_model import StockPredictionModels
        trainer = StockPredictionModels()
        
        if symbol == 'ALL':
            # Train for all stocks (this might take a while)
            stocks = data_loader.get_stock_list()
            results = {}
            
            for stock in stocks[:3]:  # Limit to first 3 for demo
                try:
                    df = data_loader.load_data()
                    stock_data = preprocessor.prepare_data_for_ml(df, stock)
                    result = trainer.train_all_models(stock_data, stock)
                    results[stock] = result
                except Exception as e:
                    results[stock] = {'error': str(e)}
        else:
            # Train for specific stock
            df = data_loader.load_data()
            stock_data = preprocessor.prepare_data_for_ml(df, symbol)
            results = trainer.train_all_models(stock_data, symbol)
        
        return jsonify({
            'success': True,
            'message': f'Models trained for {symbol}',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/portfolio/simulate', methods=['POST'])
def simulate_portfolio():
    """Simulate portfolio performance"""
    try:
        data = request.get_json()
        portfolio = data.get('portfolio', [])
        initial_amount = data.get('initial_amount', 1000000)  # TZS
        
        df = data_loader.load_data()
        simulation_results = []
        
        for stock in portfolio:
            symbol = stock.get('symbol')
            shares = stock.get('shares', 0)
            
            stock_data = data_loader.get_stock_data(symbol)
            if not stock_data.empty:
                initial_price = float(stock_data['close'].iloc[0])
                current_price = float(stock_data['close'].iloc[-1])
                
                investment = shares * initial_price
                current_value = shares * current_price
                profit_loss = current_value - investment
                profit_loss_percent = (profit_loss / investment) * 100
                
                simulation_results.append({
                    'symbol': symbol,
                    'shares': shares,
                    'initial_price': initial_price,
                    'current_price': current_price,
                    'investment': investment,
                    'current_value': current_value,
                    'profit_loss': profit_loss,
                    'profit_loss_percent': profit_loss_percent
                })
        
        # Calculate portfolio totals
        total_investment = sum(r['investment'] for r in simulation_results)
        total_value = sum(r['current_value'] for r in simulation_results)
        total_profit_loss = total_value - total_investment
        total_profit_loss_percent = (total_profit_loss / total_investment) * 100 if total_investment > 0 else 0
        
        return jsonify({
            'success': True,
            'portfolio': simulation_results,
            'summary': {
                'total_investment': total_investment,
                'total_value': total_value,
                'total_profit_loss': total_profit_loss,
                'total_profit_loss_percent': total_profit_loss_percent
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Helper functions
def get_stock_sector(symbol):
    """Get sector for a stock symbol"""
    sectors = {
        'CRDB': 'Banking',
        'NMB': 'Banking',
        'DCB': 'Banking',
        'ACB': 'Banking',
        'MICO': 'Banking',
        'TBL': 'Beverages',
        'TCC': 'Cement',
        'TWIGA': 'Cement',
        'SIMBA': 'Cement',
        'VODACOM': 'Telecommunications',
        'NICOL': 'Financial Services',
        'TPC': 'Agriculture',
        'SWISSPORT': 'Aviation',
        'JUBILEE': 'Insurance',
        'KAHE': 'Mining'
    }
    return sectors.get(symbol, 'Unknown')

def calculate_market_cap(stock_data):
    """Calculate market cap (simplified)"""
    if stock_data.empty:
        return 0
    latest_price = stock_data['close'].iloc[-1]
    latest_volume = stock_data['volume'].iloc[-1]
    return int(latest_price * latest_volume * 1000)  # Simplified calculation

def analyze_price_trend(stock_data):
    """Analyze price trend"""
    if len(stock_data) < 20:
        return {'trend': 'INSUFFICIENT_DATA'}
    
    # Calculate moving averages
    ma_5 = stock_data['close'].rolling(5).mean().iloc[-1]
    ma_20 = stock_data['close'].rolling(20).mean().iloc[-1]
    current_price = stock_data['close'].iloc[-1]
    
    # Determine trend
    if current_price > ma_5 > ma_20:
        trend = 'STRONG_UPTREND'
    elif current_price > ma_5:
        trend = 'UPTREND'
    elif current_price < ma_5 < ma_20:
        trend = 'STRONG_DOWNTREND'
    elif current_price < ma_5:
        trend = 'DOWNTREND'
    else:
        trend = 'SIDEWAYS'
    
    return {
        'trend': trend,
        'ma_5': float(ma_5),
        'ma_20': float(ma_20),
        'current_price': float(current_price)
    }

if __name__ == '__main__':
    # Initialize data
    print("🚀 Starting Tanzania Stock Market AI API...")
    print("📊 Loading market data...")
    data_loader.load_data()
    
    # Start Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
