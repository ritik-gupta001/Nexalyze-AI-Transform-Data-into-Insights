import torch
import torch.nn as nn
import numpy as np
from typing import Dict
import os

from app.core.config import get_settings
from app.core.logger import log

settings = get_settings()


class BiLSTMSentimentModel(nn.Module):
    """BiLSTM model for sentiment classification"""
    
    def __init__(self, vocab_size=10000, embedding_dim=100, hidden_dim=128, output_dim=3):
        super(BiLSTMSentimentModel, self).__init__()
        
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers=2, 
                           bidirectional=True, batch_first=True, dropout=0.3)
        self.fc = nn.Linear(hidden_dim * 2, output_dim)
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, text):
        embedded = self.dropout(self.embedding(text))
        lstm_out, (hidden, cell) = self.lstm(embedded)
        
        # Concatenate the final forward and backward hidden states
        hidden = torch.cat((hidden[-2,:,:], hidden[-1,:,:]), dim=1)
        hidden = self.dropout(hidden)
        
        output = self.fc(hidden)
        return output


class SentimentDLModel:
    """Deep Learning sentiment analysis using BiLSTM"""
    
    def __init__(self):
        self.model = None
        self.vocab = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.load_or_create_model()
    
    def load_or_create_model(self):
        """Load existing model or create a new one"""
        model_path = settings.SENTIMENT_DL_MODEL_PATH
        
        if os.path.exists(model_path):
            try:
                checkpoint = torch.load(model_path, map_location=self.device)
                self.model = BiLSTMSentimentModel()
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.vocab = checkpoint.get('vocab', self._create_vocab())
                self.model.to(self.device)
                self.model.eval()
                log.info("DL sentiment model loaded")
            except Exception as e:
                log.warning(f"Failed to load DL model: {e}. Creating new one.")
                self.create_model()
        else:
            self.create_model()
    
    def create_model(self):
        """Create and initialize a new model"""
        self.model = BiLSTMSentimentModel()
        self.vocab = self._create_vocab()
        self.model.to(self.device)
        self.model.eval()
        
        # Save model
        os.makedirs(os.path.dirname(settings.SENTIMENT_DL_MODEL_PATH), exist_ok=True)
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'vocab': self.vocab
        }, settings.SENTIMENT_DL_MODEL_PATH)
        
        log.info("DL sentiment model created and saved")
    
    def _create_vocab(self):
        """Create a simple vocabulary (in production, build from training data)"""
        common_words = [
            'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
            'good', 'bad', 'great', 'terrible', 'excellent', 'awful', 'amazing',
            'horrible', 'wonderful', 'disappointing', 'positive', 'negative',
            'happy', 'sad', 'love', 'hate', 'best', 'worst', 'nice', 'poor'
        ]
        vocab = {'<PAD>': 0, '<UNK>': 1}
        for i, word in enumerate(common_words, start=2):
            vocab[word] = i
        return vocab
    
    def text_to_indices(self, text: str, max_length: int = 100):
        """Convert text to token indices"""
        words = text.lower().split()
        indices = [self.vocab.get(word, self.vocab['<UNK>']) for word in words]
        
        # Pad or truncate
        if len(indices) < max_length:
            indices += [self.vocab['<PAD>']] * (max_length - len(indices))
        else:
            indices = indices[:max_length]
        
        return torch.tensor([indices], dtype=torch.long)
    
    def predict(self, text: str) -> Dict[str, float]:
        """
        Predict sentiment using DL model
        Returns: dict with positive, neutral, negative probabilities
        """
        try:
            if not self.model:
                self.load_or_create_model()
            
            # Prepare input
            indices = self.text_to_indices(text).to(self.device)
            
            # Get prediction
            with torch.no_grad():
                output = self.model(indices)
                probas = torch.softmax(output, dim=1).cpu().numpy()[0]
            
            # Map to sentiment
            sentiment_map = {0: "negative", 1: "neutral", 2: "positive"}
            prediction = np.argmax(probas)
            
            result = {
                "negative": float(probas[0]),
                "neutral": float(probas[1]),
                "positive": float(probas[2]),
                "label": sentiment_map[prediction],
                "confidence": float(max(probas))
            }
            
            return result
            
        except Exception as e:
            log.error(f"Error in DL sentiment prediction: {e}")
            # Fallback
            from app.ml.sentiment_ml import SentimentMLModel
            ml_model = SentimentMLModel()
            return ml_model.predict(text)
