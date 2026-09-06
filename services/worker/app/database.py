import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Ensure data directory exists
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/unividown.db")

# Parse sqlite path to ensure folder exists
if DATABASE_URL.startswith("sqlite:///"):
    db_relative_path = DATABASE_URL.replace("sqlite:///", "")
    db_file = Path(db_relative_path)
    # If run from worker directory or root directory, handle path resolution
    if not db_file.is_absolute():
        # Check if ./data or ../../data is target
        if not db_file.parent.exists():
            db_file.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
