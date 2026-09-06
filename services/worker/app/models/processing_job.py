from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    tool_type = Column(String, nullable=False)  # convert/trim/compress/merge
    status = Column(String, nullable=False, default="pending")  # pending/processing/completed/failed
    progress = Column(Float, default=0.0)
    input_files = Column(Text, nullable=False)  # JSON array of filepaths
    output_files = Column(Text, nullable=True)  # JSON array of filepaths
    parameters = Column(Text, nullable=True)  # JSON object
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "tool_type": self.tool_type,
            "status": self.status,
            "progress": self.progress,
            "input_files": self.input_files,
            "output_files": self.output_files,
            "parameters": self.parameters,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
