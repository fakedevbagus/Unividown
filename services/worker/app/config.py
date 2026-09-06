from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Unividown Worker API"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite:///./data/unividown.db"
    
    # File storage
    upload_dir: str = "./data/uploads"
    download_dir: str = "./data/downloads"
    processed_dir: str = "./data/processed"
    max_file_size: int = 10737418240  # 10GB
    
    # CORS
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Rate limiting
    rate_limit_requests: int = 60
    rate_limit_window: int = 60
    
    # Worker
    worker_url: str = "http://localhost:8000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()