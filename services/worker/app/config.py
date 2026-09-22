from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'Unividown Worker API'
    debug: bool = False
    python_env: str = 'production'
    database_url: str = 'sqlite:///./data/unividown.db'
    upload_dir: str = './data/uploads'
    download_dir: str = './data/downloads'
    processed_dir: str = './data/processed'
    max_file_size: int = 10737418240
    storage_quota_bytes: int = 53687091200
    output_retention_hours: int = 168
    cleanup_interval_seconds: int = 3600
    allowed_origins: List[str] = ['http://localhost:3000', 'http://127.0.0.1:3000']
    rate_limit_requests: int = 60
    rate_limit_window: int = 60
    worker_url: str = 'http://localhost:8000'
    redis_url: Optional[str] = 'redis://localhost:6379'
    redis_required: bool = False
    max_worker_processes: int = 3

    class Config:
        env_file = '.env'
        case_sensitive = False


settings = Settings()
