"""
Configuration settings for the OCR Receipt Processor application.
Centralizes all environment variables and application settings.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./data/receipts.db"
    
    # API Configuration
    API_HOST: str = "localhost"
    API_PORT: int = 8001
    API_TITLE: str = "OCR Receipt Processor"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Advanced OCR system for processing receipts and bills"
    
    # Dashboard Configuration
    DASHBOARD_HOST: str = "localhost"
    DASHBOARD_PORT: int = 8501
    
    # OCR Configuration
    TESSERACT_PATH: Optional[str] = None
    SUPPORTED_IMAGE_FORMATS: list = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    SUPPORTED_DOCUMENT_FORMATS: list = ['.pdf']
    SUPPORTED_TEXT_FORMATS: list = ['.txt', '.csv']
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"
    
    # Search Configuration
    DEFAULT_SEARCH_ALGORITHM: str = "linear"
    DEFAULT_SORT_ALGORITHM: str = "timsort"
    FUZZY_SEARCH_THRESHOLD: float = 0.7
    
    # Analytics Configuration
    DEFAULT_HISTOGRAM_BINS: int = 10
    TIME_SERIES_WINDOWS: list = ["daily", "weekly", "monthly"]
    
    # CORS Configuration
    ALLOWED_ORIGINS: list = ["*"]
    ALLOWED_METHODS: list = ["*"]
    ALLOWED_HEADERS: list = ["*"]
    
    # Performance Configuration
    CACHE_TTL: int = 300  # 5 minutes
    MAX_CONCURRENT_UPLOADS: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True) 