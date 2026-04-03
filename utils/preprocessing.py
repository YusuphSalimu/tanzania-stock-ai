"""
Data Preprocessing Utilities for Tanzania Stock Market AI
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

class StockDataPreprocessor:
    """Preprocess stock data for ML models"""
    
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.standard_scaler = StandardScaler()
        
    def clean_data(self, df):
        """Clean and validate stock data"""
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        df = df.fillna(method='forward').fillna(method='backward')
        
        # Remove outliers (beyond 3 standard deviations)
        for col in ['open', 'high', 'low', 'close', 'volume']:
            mean = df[col].mean()
            std = df[col].std()
            df = df[np.abs(df[col] - mean) <= 3 * std]
        
        # Sort by date
        df = df.sort_values('date')
        
        return df
    
    def add_technical_indicators(self, df):
        """Add technical indicators for better predictions"""
        df = df.copy()
        
        # Moving Averages
        df['ma_5'] = df['close'].rolling(window=5).mean()
        df['ma_10'] = df['close'].rolling(window=10).mean()
        df['ma_20'] = df['close'].rolling(window=20).mean()
        
        # Relative Strength Index (RSI)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        # Price Change
        df['price_change'] = df['close'].pct_change()
        df['price_change_5'] = df['close'].pct_change(5)
        df['price_change_10'] = df['close'].pct_change(10)
        
        # Volume indicators
        df['volume_ma'] = df['volume'].rolling(window=10).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        
        # Volatility
        df['volatility'] = df['close'].rolling(window=10).std()
        
        # Lag features
        for lag in [1, 2, 3, 5]:
            df[f'close_lag_{lag}'] = df['close'].shift(lag)
            df[f'volume_lag_{lag}'] = df['volume'].shift(lag)
        
        return df
    
    def create_sequences(self, data, sequence_length=60, target_column='close'):
        """Create sequences for time series models (LSTM)"""
        sequences = []
        targets = []
        
        for i in range(len(data) - sequence_length):
            seq = data[i:i + sequence_length]
            target = data[i + sequence_length][target_column]
            sequences.append(seq)
            targets.append(target)
        
        return np.array(sequences), np.array(targets)
    
    def prepare_data_for_ml(self, df, stock_symbol, sequence_length=60):
        """Prepare data for machine learning models"""
        # Filter for specific stock
        stock_data = df[df['stock_symbol'] == stock_symbol].copy()
        
        # Clean data
        stock_data = self.clean_data(stock_data)
        
        # Add technical indicators
        stock_data = self.add_technical_indicators(stock_data)
        
        # Remove rows with NaN values (from indicators)
        stock_data = stock_data.dropna()
        
        # Select features
        feature_columns = [
            'open', 'high', 'low', 'close', 'volume',
            'ma_5', 'ma_10', 'ma_20', 'rsi', 'macd', 'signal',
            'bb_upper', 'bb_lower', 'price_change', 'price_change_5',
            'volume_ratio', 'volatility', 'close_lag_1', 'close_lag_2'
        ]
        
        features = stock_data[feature_columns].values
        targets = stock_data['close'].values
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Create sequences for LSTM
        X_seq, y_seq = self.create_sequences(features_scaled, sequence_length)
        
        # For traditional ML models (non-sequence)
        X_train, X_test, y_train, y_test = train_test_split(
            features_scaled[:-1], targets[1:], test_size=0.2, shuffle=False
        )
        
        return {
            'stock_data': stock_data,
            'features': features_scaled,
            'targets': targets,
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
            'X_seq': X_seq,
            'y_seq': y_seq,
            'feature_columns': feature_columns,
            'scaler': self.scaler
        }
    
    def prepare_multi_stock_data(self, df, stock_symbols, sequence_length=60):
        """Prepare data for multiple stocks"""
        multi_stock_data = {}
        
        for symbol in stock_symbols:
            try:
                data = self.prepare_data_for_ml(df, symbol, sequence_length)
                multi_stock_data[symbol] = data
                print(f"✅ Prepared data for {symbol}")
            except Exception as e:
                print(f"❌ Error preparing data for {symbol}: {e}")
        
        return multi_stock_data
    
    def get_feature_importance_data(self, X, y):
        """Prepare data for feature importance analysis"""
        return train_test_split(X, y, test_size=0.2, random_state=42)

if __name__ == "__main__":
    # Test the preprocessing
    from data_loader import DSEDataLoader
    
    loader = DSEDataLoader()
    df = loader.load_data()
    
    preprocessor = StockDataPreprocessor()
    
    # Test with CRDB stock
    print("🔧 Testing data preprocessing...")
    data = preprocessor.prepare_data_for_ml(df, 'CRDB')
    
    print(f"✅ Data prepared successfully!")
    print(f"📊 Features shape: {data['features'].shape}")
    print(f"🎯 Targets shape: {data['targets'].shape}")
    print(f"📈 Sequences shape: {data['X_seq'].shape}")
    print(f"🔢 Feature columns: {len(data['feature_columns'])}")
