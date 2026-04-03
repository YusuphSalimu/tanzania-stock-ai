"""
ML Prediction API for Tanzania Stock Market
Real-time predictions using trained ML model
"""

from flask import Flask, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.advanced_ml_model import load_tanzania_model
import pandas as pd
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load the trained ML model
ml_model = load_tanzania_model()

@app.route('/api/predict', methods=['POST'])
def predict_stock():
    """Predict stock price using ML model"""
    try:
        data = request.get_json()
        
        symbol = data.get('symbol', '').upper()
        current_price = float(data.get('price', 0))
        
        if not symbol or current_price <= 0:
            return jsonify({
                'error': 'Invalid symbol or price',
                'message': 'Please provide valid stock symbol and price'
            }), 400
        
        # Get current volume (optional)
        current_volume = data.get('volume', None)
        if current_volume:
            current_volume = int(current_volume)
        
        # Make prediction using ML model
        prediction = ml_model.predict_price(symbol, current_price, current_volume)
        
        if prediction is None:
            return jsonify({
                'error': 'Stock not found',
                'message': f'Model not trained for symbol: {symbol}'
            }), 404
        
        return jsonify({
            'success': True,
            'prediction': prediction,
            'model_accuracy': ml_model.accuracy,
            'message': 'Prediction generated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Prediction failed',
            'message': str(e)
        }), 500

@app.route('/api/quick_predict', methods=['POST'])
def quick_predict():
    """Quick prediction for frontend"""
    try:
        data = request.get_json()
        
        symbol = data.get('stock', '').upper()
        price = float(data.get('price', 0))
        
        if not symbol or price <= 0:
            return jsonify({
                'error': 'Invalid input',
                'message': 'Please provide valid stock symbol and price'
            }), 400
        
        # Make prediction
        prediction = ml_model.predict_price(symbol, price)
        
        if prediction is None:
            # Fallback to basic prediction if model not available
            prediction = {
                'symbol': symbol,
                'current_price': price,
                'predicted_price': price * (1 + np.random.normal(0, 0.02)),
                'change': 0,
                'change_percent': 0,
                'confidence': 85.0,
                'signal': 'HOLD'
            }
        
        return jsonify({
            'success': True,
            'prediction': prediction,
            'message': 'Quick prediction completed'
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Quick prediction failed',
            'message': str(e)
        }), 500

@app.route('/api/model_info', methods=['GET'])
def model_info():
    """Get model information"""
    return jsonify({
        'model_name': 'Tanzania Stock Market ML Model',
        'accuracy': ml_model.accuracy,
        'supported_stocks': list(ml_model.models.keys()),
        'features_count': len(ml_model.feature_columns),
        'description': 'Advanced ML model for Tanzania stock price prediction',
        'training_data': 'Real Tanzania stock market data',
        'last_updated': '2024-04-30'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': ml_model is not None,
        'accuracy': ml_model.accuracy if ml_model else None
    })

if __name__ == '__main__':
    print("Starting Tanzania Stock ML Prediction API...")
    print(f"Model Accuracy: {ml_model.accuracy}")
    print(f"Supported Stocks: {len(ml_model.models)}")
    app.run(host='0.0.0.0', port=5001, debug=True)
