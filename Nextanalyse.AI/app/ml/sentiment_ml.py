import numpy as np
from typing import Dict, Tuple
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from app.core.config import get_settings
from app.core.logger import log

settings = get_settings()


class SentimentMLModel:
    """ML-based sentiment analysis using TF-IDF + Logistic Regression"""
    
    def __init__(self):
        self.model = None
        self.load_or_create_model()
    
    def load_or_create_model(self):
        """Load existing model or create a new one"""
        model_path = settings.SENTIMENT_ML_MODEL_PATH
        
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                log.info("ML sentiment model loaded")
            except Exception as e:
                log.warning(f"Failed to load model: {e}. Creating new one.")
                self.create_model()
        else:
            self.create_model()
    
    def create_model(self):
        """Create a pre-trained model (simplified for demo)"""
        # In production, train on real labeled dataset
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
            ('classifier', LogisticRegression(max_iter=1000, random_state=42))
        ])
        
        # Demo training data (replace with real dataset)
        demo_texts = [
            "excellent great amazing wonderful fantastic",
            "terrible awful horrible bad worst",
            "good nice positive happy satisfied",
            "poor negative disappointed unhappy",
            "okay average neutral fine normal"
        ]
        demo_labels = [2, 0, 2, 0, 1]  # 0=negative, 1=neutral, 2=positive
        
        self.model.fit(demo_texts, demo_labels)
        
        # Save model
        os.makedirs(os.path.dirname(settings.SENTIMENT_ML_MODEL_PATH), exist_ok=True)
        with open(settings.SENTIMENT_ML_MODEL_PATH, 'wb') as f:
            pickle.dump(self.model, f)
        
        log.info("ML sentiment model created and saved")
    
    def predict(self, text: str) -> Dict[str, float]:
        """
        Predict sentiment for text
        Returns: dict with positive, neutral, negative probabilities
        """
        try:
            if not self.model:
                self.load_or_create_model()
            
            # Get prediction probabilities
            proba = self.model.predict_proba([text])[0]
            
            # Map to sentiment labels
            sentiment_map = {
                0: "negative",
                1: "neutral",
                2: "positive"
            }
            
            prediction = self.model.predict([text])[0]
            
            result = {
                "negative": float(proba[0]),
                "neutral": float(proba[1]) if len(proba) > 1 else 0.0,
                "positive": float(proba[2]) if len(proba) > 2 else 0.0,
                "label": sentiment_map.get(prediction, "neutral"),
                "confidence": float(max(proba))
            }
            
            return result
            
        except Exception as e:
            log.error(f"Error in ML sentiment prediction: {e}")
            # Fallback to simple lexicon-based
            return self._lexicon_fallback(text)
    
    def _lexicon_fallback(self, text: str) -> Dict[str, float]:
        """Enhanced lexicon-based analysis for news content"""
        text_lower = text.lower()
        
        # Expanded lexicons for news analysis
        positive_words = [
            # Success & Growth
            'success', 'successful', 'growth', 'growing', 'expansion', 'increase', 'rising', 'gains',
            'profit', 'revenue', 'milestone', 'achievement', 'breakthrough', 'innovation', 'progress',
            'improvement', 'advance', 'boost', 'surge', 'soar', 'record', 'peak', 'high',
            # Quality & Performance
            'excellent', 'outstanding', 'exceptional', 'impressive', 'strong', 'robust', 'solid',
            'good', 'great', 'positive', 'optimistic', 'confident', 'favorable', 'promising',
            'effective', 'efficient', 'productive', 'valuable', 'beneficial', 'advantage',
            # Development & Investment
            'development', 'investment', 'funding', 'capital', 'initiative', 'launch', 'unveil',
            'opportunity', 'potential', 'prospects', 'momentum', 'confidence', 'optimism',
            # Infrastructure & Quality of Life
            'modernization', 'upgrade', 'enhancement', 'improvement', 'infrastructure', 'facilities',
            'connectivity', 'accessibility', 'sustainable', 'green', 'clean', 'eco-friendly'
        ]
        
        negative_words = [
            # Problems & Decline
            'decline', 'decrease', 'fall', 'drop', 'plunge', 'crash', 'collapse', 'failure',
            'loss', 'losses', 'deficit', 'debt', 'crisis', 'recession', 'downturn', 'slump',
            'weak', 'poor', 'disappointing', 'missed', 'below', 'underperform',
            # Challenges & Issues
            'concern', 'concerns', 'worry', 'worries', 'risk', 'risks', 'threat', 'challenge',
            'problem', 'problems', 'issue', 'issues', 'difficulty', 'struggle', 'setback',
            'delay', 'postpone', 'cancel', 'suspend', 'halt', 'stop',
            # Negative conditions
            'pollution', 'congestion', 'corruption', 'scandal', 'controversy', 'violation',
            'shortage', 'scarcity', 'crisis', 'emergency', 'disaster', 'damage',
            'bad', 'terrible', 'awful', 'horrible', 'worst', 'negative', 'criticism'
        ]
        
        neutral_modifiers = [
            # Balanced/Mixed indicators
            'mixed', 'varied', 'stable', 'steady', 'unchanged', 'maintained', 'continued',
            'moderate', 'gradual', 'cautious', 'awaiting', 'expected', 'projected',
            'analysts', 'experts', 'officials', 'sources', 'reports', 'according'
        ]
        
        # Count occurrences with context awareness
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        neutral_count = sum(1 for word in neutral_modifiers if word in text_lower)
        
        # Check for specific patterns
        if 'despite' in text_lower or 'however' in text_lower or 'but' in text_lower:
            # Mixed sentiment - reduce confidence
            neutral_count += 2
        
        if 'record' in text_lower and ('high' in text_lower or 'growth' in text_lower):
            pos_count += 2  # Strong positive signal
        
        if 'sharp correction' in text_lower or 'profit-taking' in text_lower:
            neg_count += 1  # Market downturn
        
        # Calculate probabilities with better distribution
        total = max(pos_count + neg_count + neutral_count, 1)
        
        pos_prob = pos_count / total
        neg_prob = neg_count / total
        neutral_prob = max(neutral_count / total, 0.1)  # Minimum 10% neutral
        
        # Normalize to sum to 1.0
        total_prob = pos_prob + neg_prob + neutral_prob
        if total_prob > 0:
            pos_prob /= total_prob
            neg_prob /= total_prob
            neutral_prob /= total_prob
        else:
            # Default neutral
            pos_prob, neg_prob, neutral_prob = 0.33, 0.33, 0.34
        
        # Determine overall label
        max_prob = max(pos_prob, neg_prob, neutral_prob)
        if pos_prob == max_prob:
            label = "positive"
        elif neg_prob == max_prob:
            label = "negative"
        else:
            label = "neutral"
        
        return {
            "positive": float(pos_prob),
            "negative": float(neg_prob),
            "neutral": float(neutral_prob),
            "label": label,
            "confidence": float(max_prob)
        }
    
    def batch_predict(self, texts: list) -> list:
        """Predict sentiment for multiple texts"""
        return [self.predict(text) for text in texts]
