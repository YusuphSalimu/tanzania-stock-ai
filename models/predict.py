"""
Stock Price Prediction System
Uses trained models to make predictions
"""

import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
from datetime import datetime, timedelta
import json
import os

class StockPredictor:
    """Advanced stock price prediction system"""
    
    def __init__(self, model_dir="models"):
        self.model_dir = model_dir
        self.models = {}
        self.scalers = {}
        
    def load_model(self, stock_symbol, model_type='best'):
        """Load trained model for prediction"""
        try:
            if model_type == 'best':
                # Get the best model for this stock
                metrics_path = f"{self.model_dir}/metrics_{stock_symbol.lower()}.json"
                with open(metrics_path, 'r') as f:
                    metrics = json.load(f)
                
                best_model = max(metrics.keys(), key=lambda k: metrics[k]['r2'])
                model_type = best_model
            
            # Load the specific model
            if model_type == 'lstm':
                model_path = f"{self.model_dir}/lstm_{stock_symbol.lower()}.h5"
                model = tf.keras.models.load_model(model_path)
            elif model_type == 'xgboost':
                model_path = f"{self.model_dir}/xgb_{stock_symbol.lower()}.pkl"
                model = joblib.load(model_path)
            elif model_type == 'random_forest':
                model_path = f"{self.model_dir}/rf_{stock_symbol.lower()}.pkl"
                model = joblib.load(model_path)
            else:
                raise ValueError(f"Unknown model type: {model_type}")
            
            self.models[f"{stock_symbol}_{model_type}"] = model
            print(f"✅ Loaded {model_type} model for {stock_symbol}")
            return model
            
        except FileNotFoundError:
            print(f"❌ Model not found for {stock_symbol}")
            return None
    
    def load_scaler(self, stock_symbol):
        """Load the scaler for data preprocessing"""
        try:
            scaler_path = f"{self.model_dir}/scaler_{stock_symbol.lower()}.pkl"
            scaler = joblib.load(scaler_path)
            self.scalers[stock_symbol] = scaler
            return scaler
        except FileNotFoundError:
            print(f"⚠️ Scaler not found for {stock_symbol}, using default")
            from sklearn.preprocessing import MinMaxScaler
            return MinMaxScaler()
    
    def predict_next_day(self, data, stock_symbol, model_type='best'):
        """Predict next day's stock price"""
        try:
            # Load model
            model = self.load_model(stock_symbol, model_type)
            if model is None:
                return None
            
            # Prepare data for prediction
            if model_type == 'lstm':
                # LSTM needs sequence data
                last_sequence = data['X_seq'][-1:] if len(data['X_seq']) > 0 else None
                if last_sequence is None:
                    return None
                
                prediction = model.predict(last_sequence)
                predicted_price = prediction[0][0]
                
            else:
                # XGBoost and Random Forest use regular features
                last_features = data['X_test'][-1:] if len(data['X_test']) > 0 else None
                if last_features is None:
                    return None
                
                prediction = model.predict(last_features)
                predicted_price = prediction[0]
            
            # Inverse transform to get actual price
            scaler = data.get('scaler')
            if scaler:
                # Create a dummy array with same shape as features
                dummy_features = np.zeros((1, len(data['feature_columns'])))
                dummy_features[0, -1] = predicted_price  # Put prediction in last position
                
                # Inverse transform
                inverse_scaled = scaler.inverse_transform(dummy_features)
                predicted_price = inverse_scaled[0, -1]
            
            return predicted_price
            
        except Exception as e:
            return None
    
    def predict_multiple_days(self, data, stock_symbol, days=7, model_type='best'):
        """Predict stock prices for multiple days"""
        predictions = []
        current_data = data.copy()
        
        for day in range(days):
            prediction = self.predict_next_day(current_data, stock_symbol, model_type)
            if prediction is None:
                break
            
            predictions.append(prediction)
            
            # Update data for next prediction (simplified approach)
            # In production, you'd want to properly update the feature set
            if 'X_test' in current_data and len(current_data['X_test']) > 0:
                # Shift data and add new prediction
                new_features = current_data['X_test'][-1:].copy()
                new_features[0, -1] = prediction  # Update close price
                current_data['X_test'] = np.vstack([current_data['X_test'][1:], new_features])
        
        return predictions
    
    def get_prediction_confidence(self, data, stock_symbol, model_type='best'):
        """Get prediction confidence based on model performance"""
        try:
            metrics_path = f"{self.model_dir}/metrics_{stock_symbol.lower()}.json"
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
            
            if model_type == 'best':
                # Get best model metrics
                best_model = max(metrics.keys(), key=lambda k: metrics[k]['r2'])
                model_metrics = metrics[best_model]
            else:
                model_metrics = metrics.get(model_type, {})
            
            # Calculate confidence based on R² score
            r2_score = model_metrics.get('r2', 0)
            confidence = min(max(r2_score * 100, 0), 95)  # Cap at 95%
            
            return confidence, model_metrics
            
        except FileNotFoundError:
            return 50, {}  # Default confidence
    
    def generate_trading_signal(self, current_price, predicted_price, confidence):
        """Generate buy/sell/hold signal"""
        if confidence < 60:
            return "HOLD", "Low confidence in prediction"
        
        price_change_percent = ((predicted_price - current_price) / current_price) * 100
        
        if price_change_percent > 2:
            return "BUY", f"Expected increase of {price_change_percent:.2f}%"
        elif price_change_percent < -2:
            return "SELL", f"Expected decrease of {abs(price_change_percent):.2f}%"
        else:
            return "HOLD", f"Minimal change expected ({price_change_percent:.2f}%)"
    
    def get_risk_assessment(self, data, stock_symbol):
        """Assess investment risk for a stock"""
        try:
            stock_data = data['stock_data']
            
            # Calculate volatility
            returns = stock_data['close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)  # Annualized volatility
            
            # Calculate max drawdown
            peak = stock_data['close'].expanding().max()
            drawdown = (stock_data['close'] - peak) / peak
            max_drawdown = drawdown.min()
            
            # Risk categories
            if volatility < 0.15:
                risk_level = "LOW"
            elif volatility < 0.25:
                risk_level = "MEDIUM"
            else:
                risk_level = "HIGH"
            
            return {
                'volatility': volatility,
                'max_drawdown': max_drawdown,
                'risk_level': risk_level,
                'risk_score': min(volatility * 100, 100)
            }
            
        except Exception as e:
            return {'risk_level': 'UNKNOWN', 'risk_score': 50}
    
    def generate_full_report(self, data, stock_symbol, model_type='best'):
        """Generate comprehensive prediction report"""
        # Get current price
        current_price = data['stock_data']['close'].iloc[-1]
        
        # Get predictions
        next_day_prediction = self.predict_next_day(data, stock_symbol, model_type)
        week_predictions = self.predict_multiple_days(data, stock_symbol, 7, model_type)
        
        # Get confidence
        confidence, metrics = self.get_prediction_confidence(data, stock_symbol, model_type)
        
        # Generate trading signal
        if next_day_prediction:
            signal, signal_reason = self.generate_trading_signal(
                current_price, next_day_prediction, confidence
            )
        else:
            signal, signal_reason = "HOLD", "Prediction unavailable"
        
        # Risk assessment
        risk_assessment = self.get_risk_assessment(data, stock_symbol)
        
        # Create report
        report = {
            'stock_symbol': stock_symbol,
            'current_price': round(current_price, 2),
            'predicted_price': round(next_day_prediction, 2) if next_day_prediction else None,
            'price_change': round(next_day_prediction - current_price, 2) if next_day_prediction else None,
            'price_change_percent': round(((next_day_prediction - current_price) / current_price) * 100, 2) if next_day_prediction else None,
            'trading_signal': signal,
            'signal_reason': signal_reason,
            'confidence': round(confidence, 2),
            'week_predictions': [round(p, 2) for p in week_predictions] if week_predictions else [],
            'model_metrics': metrics,
            'risk_assessment': risk_assessment,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'model_used': model_type
        }
        
        return report

if __name__ == "__main__":
    # Test prediction system
    from utils.data_loader import DSEDataLoader
    from utils.preprocessing import StockDataPreprocessor
    
    # Load and prepare data
    loader = DSEDataLoader()
    df = loader.load_data()
    
    preprocessor = StockDataPreprocessor()
    data = preprocessor.prepare_data_for_ml(df, 'CRDB')
    
    # Create predictor
    predictor = StockPredictor()
    
    # Generate report
    report = predictor.generate_full_report(data, 'CRDB')
    
    print("📊 Prediction Report:")
    print(json.dumps(report, indent=2))
