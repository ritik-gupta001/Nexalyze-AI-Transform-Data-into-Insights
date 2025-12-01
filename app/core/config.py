from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "PRA - Personal Research Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite:///./pra_database.db"
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_TEMPERATURE: float = 0.7
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    REPORTS_DIR: str = "./app/reports"
    CHARTS_DIR: str = "./app/charts"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # Model Paths
    SENTIMENT_ML_MODEL_PATH: str = "./models/sentiment_ml.pkl"
    SENTIMENT_DL_MODEL_PATH: str = "./models/sentiment_dl.pth"
    FORECAST_MODEL_PATH: str = "./models/forecast_model.pkl"
    
    # Agent Settings
    MAX_AGENT_ITERATIONS: int = 10
    AGENT_TIMEOUT: int = 300
    
    # News API
    NEWS_API_KEY: str = ""
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/pra.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Create necessary directories
def create_directories():
    """Create required directories if they don't exist"""
    settings = get_settings()
    dirs = [
        settings.UPLOAD_DIR,
        settings.REPORTS_DIR,
        settings.CHARTS_DIR,
        "logs",
        "models",
        "data"
    ]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
