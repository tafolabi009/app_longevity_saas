import os
from pathlib import Path
from typing import Optional, List
from pydantic import BaseSettings, EmailStr, validator
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    # Base settings
    APP_NAME: str = "App Longevity Predictor"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development_secret_key_change_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./app_longevity.db"
    )
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        # Handle Heroku PostgreSQL URLs which start with postgres://
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql://", 1)
        return v
    
    # CORS
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",  # React dev server
        "http://localhost:8000",  # FastAPI dev server
        "http://localhost",
        "https://localhost",
        "https://app-longevity-predictor.netlify.app",  # Netlify domain
        "https://app-longevity-saas.netlify.app",       # Alternative Netlify domain
        "https://app-longevity-predictor.vercel.app",
    ]
    
    # Email settings for future use
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Model settings
    MODEL_PATH: str = os.path.join("static", "models")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "rf_model.joblib")
    # Additional model paths to search (comma-separated list in env var)
    ADDITIONAL_MODEL_PATHS: List[str] = [
        path.strip() for path in os.getenv("ADDITIONAL_MODEL_PATHS", "").split(",")
        if path.strip()
    ]
    
    # Model file extensions to search for
    MODEL_FILE_EXTENSIONS: List[str] = [".joblib", ".pkl", ".h5", ".keras"]
    
    # Features
    ALLOW_REGISTRATION: bool = True
    REQUIRE_EMAIL_VALIDATION: bool = False  # Set to True in production
    
    # Service limits for free tier
    FREE_PREDICTIONS_PER_DAY: int = 10
    
    class Config:
        case_sensitive = True

settings = Settings() 
