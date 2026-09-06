# Phase 02: Database & Models

## Objective
Setup database schema dan ORM models.

## Steps

### 1. Create Database Config (services/worker/app/database.py)
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./data/unividown.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 2. Create Models (services/worker/app/models/)

**download_job.py:**
```python
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class DownloadJob(Base):
    __tablename__ = "download_jobs"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    platform = Column(String)
    title = Column(String)
    thumbnail_url = Column(String)
    status = Column(String, nullable=False, default="pending")
    progress = Column(Float, default=0.0)
    priority = Column(Integer, default=0)
    quality = Column(String)
    bitrate = Column(Integer)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
```

**downloaded_file.py:**
```python
class DownloadedFile(Base):
    __tablename__ = "downloaded_files"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer)
```

**processing_job.py:**
```python
class ProcessingJob(Base):
    __tablename__ = "processing_jobs"
    id = Column(Integer, primary_key=True)
    tool_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    progress = Column(Float, default=0.0)
    input_files = Column(Text, nullable=False)
    output_files = Column(Text)
    parameters = Column(Text)
    error_message = Column(Text)
```

### 3. Initialize Database
```python
# In main.py
Base.metadata.create_all(bind=engine)
```

## Expected Output
- Database file created at data/unividown.db
- All tables created
- Models ready for use
