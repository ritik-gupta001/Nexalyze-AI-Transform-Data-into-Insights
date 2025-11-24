import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_analyze_text():
    """Test text analysis endpoint"""
    payload = {
        "query": "Analyze sentiment about Tesla stock",
        "entity": "Tesla",
        "time_range": "last_3_days"
    }
    response = client.post("/api/v1/tasks/analyze-text", json=payload)
    assert response.status_code == 200
    assert "task_id" in response.json()
    assert response.json()["status"] in ["completed", "processing"]


def test_list_tasks():
    """Test task listing endpoint"""
    response = client.get("/api/v1/tasks/")
    assert response.status_code == 200
    assert "tasks" in response.json()
    assert "total" in response.json()
