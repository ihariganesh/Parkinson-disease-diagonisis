from typing import List
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://parkinson_user:parkinson123@localhost:5432/parkinson_db"
    DATABASE_TEST_URL: str = "postgresql://parkinson_user:parkinson123@localhost:5432/parkinson_test_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "parkinson-app-storage"
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:5174"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # File upload
    MAX_FILE_SIZE: int = 104857600  # 100MB
    UPLOAD_DIR: str = "./uploads"
    
    # ML Models
    MODEL_PATH: str = "./models"
    ENABLE_GPU: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()