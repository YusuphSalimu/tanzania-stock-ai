"""
Machine Learning Models for Tanzania Stock Market Prediction
LSTM, XGBoost, and Random Forest implementations
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import joblib
import os
import json
from datetime import datetime

class StockPredictionModels:
    """Advanced ML models for stock price prediction"""
    
    def __init__(self, model_dir="models"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # Initialize models
        self.lstm_model = None
        self.xgb_model = None
        self.rf_model = None
        
        # Model performance tracking
        self.performance_metrics = {}
    
    def build_lstm_model(self, input_shape, units=50, dropout_rate=0.2):
        """Build advanced LSTM model for stock prediction"""
        model = Sequential([
            # First LSTM layer
            Bidirectional(LSTM(units, return_sequences=True, input_shape=input_shape)),
            Dropout(dropout_rate),
            
            # Second LSTM layer
            Bidirectional(LSTM(units, return_sequences=True)),
            Dropout(dropout_rate),
            
            # Third LSTM layer
            Bidirectional(LSTM(units, return_sequences=False)),
            Dropout(dropout_rate),
            
            # Dense layers
            Dense(25, activation='relu'),
            Dropout(dropout_rate),
            Dense(10, activation='relu'),
            Dense(1)  # Output layer for price prediction
        ])
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae', 'mape']
        )
        
        return model
    
    def train_lstm(self, X_train, y_train, X_test, y_test, stock_symbol, epochs=100, batch_size=32):
        """Train LSTM model for stock prediction"""
        print(f"🧠 Training LSTM model for {stock_symbol}...")
        
        # Build model
        input_shape = (X_train.shape[1], X_train.shape[2])
        self.lstm_model = self.build_lstm_model(input_shape)
        
        # Callbacks
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.2,
            patience=5,
            min_lr=0.00001
        )
        
        # Train model
        history = self.lstm_model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stopping, reduce_lr],
            verbose=1
        )
        
        # Evaluate model
        predictions = self.lstm_model.predict(X_test)
        
        metrics = {
            'mse': mean_squared_error(y_test, predictions),
            'mae': mean_absolute_error(y_test, predictions),
            'rmse': np.sqrt(mean_squared_error(y_test, predictions)),
            'r2': r2_score(y_test, predictions),
            'mape': np.mean(np.abs((y_test - predictions) / y_test)) * 100
        }
        
        # Save model and metrics
        model_path = f"{self.model_dir}/lstm_{stock_symbol.lower()}.h5"
        self.lstm_model.save(model_path)
        
        self.performance_metrics[f'lstm_{stock_symbol}'] = metrics
        
        print(f"✅ LSTM model saved for {stock_symbol}")
        print(f"📊 LSTM RMSE: {metrics['rmse']:.2f}")
        print(f"📈 LSTM R²: {metrics['r2']:.4f}")
        
        return self.lstm_model, history, metrics
    
    def train_xgboost(self, X_train, y_train, X_test, y_test, stock_symbol):
        """Train XGBoost model for stock prediction"""
        print(f"🚀 Training XGBoost model for {stock_symbol}...")
        
        # XGBoost parameters optimized for stock prediction
        params = {
            'objective': 'reg:squarederror',
            'n_estimators': 1000,
            'max_depth': 6,
            'learning_rate': 0.01,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42,
            'n_jobs': -1
        }
        
        # Train model
        self.xgb_model = xgb.XGBRegressor(**params)
        
        # Fit with early stopping
        self.xgb_model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            early_stopping_rounds=50,
            verbose=False
        )
        
        # Predictions
        predictions = self.xgb_model.predict(X_test)
        
        # Metrics
        metrics = {
            'mse': mean_squared_error(y_test, predictions),
            'mae': mean_absolute_error(y_test, predictions),
            'rmse': np.sqrt(mean_squared_error(y_test, predictions)),
            'r2': r2_score(y_test, predictions),
            'mape': np.mean(np.abs((y_test - predictions) / y_test)) * 100
        }
        
        # Save model
        model_path = f"{self.model_dir}/xgb_{stock_symbol.lower()}.pkl"
        joblib.dump(self.xgb_model, model_path)
        
        self.performance_metrics[f'xgb_{stock_symbol}'] = metrics
        
        print(f"✅ XGBoost model saved for {stock_symbol}")
        print(f"📊 XGBoost RMSE: {metrics['rmse']:.2f}")
        print(f"📈 XGBoost R²: {metrics['r2']:.4f}")
        
        return self.xgb_model, metrics
    
    def train_random_forest(self, X_train, y_train, X_test, y_test, stock_symbol):
        """Train Random Forest model for stock prediction"""
        print(f"🌲 Training Random Forest model for {stock_symbol}...")
        
        # Random Forest parameters
        params = {
            'n_estimators': 500,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'random_state': 42,
            'n_jobs': -1
        }
        
        # Train model
        self.rf_model = RandomForestRegressor(**params)
        self.rf_model.fit(X_train, y_train)
        
        # Predictions
        predictions = self.rf_model.predict(X_test)
        
        # Metrics
        metrics = {
            'mse': mean_squared_error(y_test, predictions),
            'mae': mean_absolute_error(y_test, predictions),
            'rmse': np.sqrt(mean_squared_error(y_test, predictions)),
            'r2': r2_score(y_test, predictions),
            'mape': np.mean(np.abs((y_test - predictions) / y_test)) * 100
        }
        
        # Save model
        model_path = f"{self.model_dir}/rf_{stock_symbol.lower()}.pkl"
        joblib.dump(self.rf_model, model_path)
        
        self.performance_metrics[f'rf_{stock_symbol}'] = metrics
        
        print(f"✅ Random Forest model saved for {stock_symbol}")
        print(f"📊 Random Forest RMSE: {metrics['rmse']:.2f}")
        print(f"📈 Random Forest R²: {metrics['r2']:.4f}")
        
        return self.rf_model, metrics
    
    def train_all_models(self, data, stock_symbol):
        """Train all three models for a stock"""
        print(f"🎯 Training all models for {stock_symbol}...")
        
        results = {}
        
        # Train LSTM (uses sequence data)
        if 'X_seq' in data and len(data['X_seq']) > 0:
            try:
                lstm_model, history, lstm_metrics = self.train_lstm(
                    data['X_seq'], data['y_seq'], 
                    data['X_seq'][-100:], data['y_seq'][-100:],
                    stock_symbol
                )
                results['lstm'] = lstm_metrics
            except Exception as e:
                print(f"❌ LSTM training failed: {e}")
        
        # Train XGBoost (uses regular features)
        try:
            xgb_model, xgb_metrics = self.train_xgboost(
                data['X_train'], data['y_train'],
                data['X_test'], data['y_test'],
                stock_symbol
            )
            results['xgboost'] = xgb_metrics
        except Exception as e:
            print(f"❌ XGBoost training failed: {e}")
        
        # Train Random Forest
        try:
            rf_model, rf_metrics = self.train_random_forest(
                data['X_train'], data['y_train'],
                data['X_test'], data['y_test'],
                stock_symbol
            )
            results['random_forest'] = rf_metrics
        except Exception as e:
            print(f"❌ Random Forest training failed: {e}")
        
        # Save performance metrics
        metrics_path = f"{self.model_dir}/metrics_{stock_symbol.lower()}.json"
        with open(metrics_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def get_best_model(self, stock_symbol):
        """Get the best performing model for a stock"""
        metrics_path = f"{self.model_dir}/metrics_{stock_symbol.lower()}.json"
        
        try:
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
            
            # Find best model based on R² score
            best_model = max(metrics.keys(), key=lambda k: metrics[k]['r2'])
            best_score = metrics[best_model]['r2']
            
            return best_model, best_score, metrics
        except FileNotFoundError:
            return None, None, {}
    
    def save_performance_report(self):
        """Save overall performance report"""
        report_path = f"{self.model_dir}/performance_report.json"
        
        with open(report_path, 'w') as f:
            json.dump(self.performance_metrics, f, indent=2)
        
        print(f"📄 Performance report saved to {report_path}")

if __name__ == "__main__":
    # Test model training
    from utils.data_loader import DSEDataLoader
    from utils.preprocessing import StockDataPreprocessor
    
    # Load and prepare data
    loader = DSEDataLoader()
    df = loader.load_data()
    
    preprocessor = StockDataPreprocessor()
    data = preprocessor.prepare_data_for_ml(df, 'CRDB')
    
    # Train models
    trainer = StockPredictionModels()
    results = trainer.train_all_models(data, 'CRDB')
    
    print("\n🎉 Training completed!")
    print("📊 Results:")
    for model, metrics in results.items():
        print(f"  {model}: R² = {metrics['r2']:.4f}, RMSE = {metrics['rmse']:.2f}")
