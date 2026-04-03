"""
Tanzania Stock Exchange Data Loader
Collects and processes stock data from DSE listed companies
"""

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
import json
import os

class DSEDataLoader:
    """Dar es Salaam Stock Exchange Data Collection System"""
    
    def __init__(self):
        self.dse_stocks = {
            'CRDB': 'CRDB Bank Plc',
            'NMB': 'NMB Bank Plc',
            'TBL': 'Tanzania Breweries Limited',
            'TCC': 'Tanga Cement Company Limited',
            'TWIGA': 'Twiga Cement Company Limited',
            'VODACOM': 'Vodacom Tanzania Plc',
            'DCB': 'DCB Commercial Bank Plc',
            'ACB': 'Azania Bank Plc',
            'NICOL': 'NICOL Securities Limited',
            'TPC': 'Tanzania Plantation Company Limited',
            'SWISSPORT': 'Swissport Tanzania Limited',
            'JUBILEE': 'Jubilee Insurance Company Limited',
            'KAHE': 'Kahama Mining Corporation Limited',
            'SIMBA': 'Simba Cement Company Limited',
            'MICO': 'Mwalimu Commercial Bank Plc'
        }
        
        self.base_url = "https://www.dse.co.tz"
        self.data_dir = "data/raw"
        
    def create_sample_dataset(self):
        """Create realistic sample dataset for DSE stocks"""
        print("Creating sample dataset for DSE stocks...")
        
        # Create sample data for the past 2 years
        start_date = datetime(2022, 1, 1)
        end_date = datetime(2024, 1, 1)
        
        all_data = []
        
        for stock_symbol, company_name in self.dse_stocks.items():
            print(f"Generating data for {stock_symbol} - {company_name}")
            
            # Base price for each stock (realistic TZS values)
            base_prices = {
                'CRDB': 450, 'NMB': 2800, 'TBL': 8500, 'TCC': 3500,
                'TWIGA': 4200, 'VODACOM': 6500, 'DCB': 500, 'ACB': 300,
                'NICOL': 1500, 'TPC': 1200, 'SWISSPORT': 2800, 'JUBILEE': 1800,
                'KAHE': 800, 'SIMBA': 3200, 'MICO': 400
            }
            
            base_price = base_prices.get(stock_symbol, 1000)
            
            current_date = start_date
            while current_date <= end_date:
                # Skip weekends
                if current_date.weekday() < 5:
                    # Add realistic price movements
                    price_change = np.random.normal(0, 0.02)  # 2% daily volatility
                    trend = 0.0001 * (current_date - start_date).days  # Slight upward trend
                    
                    # Calculate OHLC
                    open_price = base_price * (1 + np.random.normal(0, 0.01))
                    close_price = open_price * (1 + price_change + trend)
                    high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.005)))
                    low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.005)))
                    
                    # Volume (realistic for DSE)
                    volume = int(np.random.lognormal(8, 1))  # Average around 3,000 shares
                    
                    all_data.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'stock_symbol': stock_symbol,
                        'company_name': company_name,
                        'open': round(open_price, 2),
                        'high': round(high_price, 2),
                        'low': round(low_price, 2),
                        'close': round(close_price, 2),
                        'volume': volume,
                        'change': round(close_price - open_price, 2),
                        'change_percent': round(((close_price - open_price) / open_price) * 100, 2)
                    })
                    
                    base_price = close_price  # Update base price for next day
                
                current_date += timedelta(days=1)
        
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Save to CSV
        os.makedirs(self.data_dir, exist_ok=True)
        df.to_csv(f'{self.data_dir}/dse_stock_data.csv', index=False)
        
        print(f"✅ Created dataset with {len(df)} records for {len(self.dse_stocks)} stocks")
        print(f"📊 Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"💾 Saved to: {self.data_dir}/dse_stock_data.csv")
        
        return df
    
    def load_data(self):
        """Load the DSE stock data"""
        try:
            df = pd.read_csv(f'{self.data_dir}/dse_stock_data.csv')
            df['date'] = pd.to_datetime(df['date'])
            return df
        except FileNotFoundError:
            print("❌ Data file not found. Creating sample dataset...")
            return self.create_sample_dataset()
    
    def get_stock_data(self, symbol):
        """Get data for a specific stock"""
        df = self.load_data()
        return df[df['stock_symbol'] == symbol]
    
    def get_stock_list(self):
        """Get list of all available stocks"""
        return list(self.dse_stocks.keys())
    
    def get_market_summary(self):
        """Get market summary statistics"""
        df = self.load_data()
        latest_date = df['date'].max()
        latest_data = df[df['date'] == latest_date]
        
        summary = {
            'date': latest_date.strftime('%Y-%m-%d'),
            'total_stocks': len(latest_data),
            'total_volume': latest_data['volume'].sum(),
            'gainers': len(latest_data[latest_data['change_percent'] > 0]),
            'losers': len(latest_data[latest_data['change_percent'] < 0]),
            'unchanged': len(latest_data[latest_data['change_percent'] == 0])
        }
        
        return summary

if __name__ == "__main__":
    loader = DSEDataLoader()
    data = loader.create_sample_dataset()
    print("\n📈 Sample data preview:")
    print(data.head())
    print("\n📊 Market summary:")
    print(loader.get_market_summary())
