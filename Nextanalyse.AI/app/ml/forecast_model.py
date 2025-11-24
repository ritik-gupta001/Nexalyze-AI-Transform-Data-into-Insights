import numpy as np
from typing import List, Tuple, Dict
import pickle
import os
from sklearn.linear_model import LinearRegression

from app.core.config import get_settings
from app.core.logger import log

settings = get_settings()


class TrendForecastModel:
    """Simple trend forecasting using linear regression"""
    
    def __init__(self):
        self.model = None
        self.load_or_create_model()
    
    def load_or_create_model(self):
        """Load or create forecast model"""
        model_path = settings.FORECAST_MODEL_PATH
        
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                log.info("Forecast model loaded")
            except Exception as e:
                log.warning(f"Failed to load forecast model: {e}")
                self.create_model()
        else:
            self.create_model()
    
    def create_model(self):
        """Create a new forecast model"""
        self.model = LinearRegression()
        
        # Save model
        os.makedirs(os.path.dirname(settings.FORECAST_MODEL_PATH), exist_ok=True)
        with open(settings.FORECAST_MODEL_PATH, 'wb') as f:
            pickle.dump(self.model, f)
        
        log.info("Forecast model created")
    
    def predict_trend(
        self, 
        sentiment_scores: List[float], 
        forecast_days: int = 7
    ) -> Tuple[List[float], str]:
        """
        Predict sentiment trend for next N days
        
        Args:
            sentiment_scores: Historical sentiment scores (positive scale)
            forecast_days: Number of days to forecast
        
        Returns:
            Tuple of (forecasted values, trend description)
        """
        try:
            if len(sentiment_scores) < 3:
                # Not enough data for prediction
                avg = np.mean(sentiment_scores) if sentiment_scores else 0.5
                return [avg] * forecast_days, "stable"
            
            # Prepare data
            X = np.array(range(len(sentiment_scores))).reshape(-1, 1)
            y = np.array(sentiment_scores)
            
            # Fit model
            self.model.fit(X, y)
            
            # Predict future
            future_X = np.array(range(len(sentiment_scores), len(sentiment_scores) + forecast_days)).reshape(-1, 1)
            predictions = self.model.predict(future_X)
            
            # Clip predictions to [0, 1] range
            predictions = np.clip(predictions, 0, 1)
            
            # Determine trend
            slope = self.model.coef_[0]
            if slope > 0.01:
                trend = "improving"
            elif slope < -0.01:
                trend = "declining"
            else:
                trend = "stable"
            
            return predictions.tolist(), trend
            
        except Exception as e:
            log.error(f"Error in trend forecasting: {e}")
            avg = np.mean(sentiment_scores) if sentiment_scores else 0.5
            return [avg] * forecast_days, "stable"
    
    def forecast_sentiment(
        self,
        historical_sentiments: List[Dict[str, float]],
        forecast_days: int = 7
    ) -> str:
        """
        Generate forecast description from sentiment history
        
        Args:
            historical_sentiments: List of sentiment dicts with 'positive' scores
            forecast_days: Days to forecast
        
        Returns:
            Human-readable forecast description
        """
        try:
            # Extract positive scores
            scores = [s.get('positive', 0.5) for s in historical_sentiments]
            
            # Get predictions
            predictions, trend = self.predict_trend(scores, forecast_days)
            
            # Generate description
            current_avg = np.mean(scores[-3:]) if len(scores) >= 3 else np.mean(scores)
            future_avg = np.mean(predictions)
            
            change_pct = ((future_avg - current_avg) / current_avg * 100) if current_avg > 0 else 0
            
            description = f"Based on recent sentiment analysis, the trend is **{trend}**. "
            
            if trend == "improving":
                description += f"Sentiment is expected to improve by approximately {abs(change_pct):.1f}% "
                description += f"over the next {forecast_days} days. Positive outlook."
            elif trend == "declining":
                description += f"Sentiment is expected to decline by approximately {abs(change_pct):.1f}% "
                description += f"over the next {forecast_days} days. Caution advised."
            else:
                description += f"Sentiment is expected to remain relatively stable "
                description += f"over the next {forecast_days} days."
            
            return description
            
        except Exception as e:
            log.error(f"Error generating forecast: {e}")
            return "Insufficient data for reliable trend forecasting."


def detect_anomalies(data: np.ndarray, threshold: float = 2.0) -> List[int]:
    """
    Detect anomalies in data using z-score method
    
    Args:
        data: Input data array
        threshold: Z-score threshold for anomaly detection
    
    Returns:
        List of anomaly indices
    """
    try:
        if len(data) < 3:
            return []
        
        mean = np.mean(data)
        std = np.std(data)
        
        if std == 0:
            return []
        
        z_scores = np.abs((data - mean) / std)
        anomalies = np.where(z_scores > threshold)[0].tolist()
        
        return anomalies
        
    except Exception as e:
        log.error(f"Error detecting anomalies: {e}")
        return []
