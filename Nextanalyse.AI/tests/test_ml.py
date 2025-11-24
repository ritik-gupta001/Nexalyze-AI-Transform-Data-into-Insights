import pytest
from app.ml.sentiment_ml import SentimentMLModel


def test_sentiment_ml_model():
    """Test ML sentiment model"""
    model = SentimentMLModel()
    
    # Test positive text
    result = model.predict("This is an excellent and amazing product!")
    assert "positive" in result
    assert "negative" in result
    assert "label" in result
    
    # Test negative text
    result = model.predict("This is terrible and awful!")
    assert result["label"] in ["positive", "negative", "neutral"]


def test_batch_predict():
    """Test batch prediction"""
    model = SentimentMLModel()
    texts = [
        "Great product!",
        "Terrible experience",
        "It's okay"
    ]
    results = model.batch_predict(texts)
    assert len(results) == 3
    assert all("label" in r for r in results)
