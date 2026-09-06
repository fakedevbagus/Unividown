from sqlalchemy import Column, Integer, String
from app.database import Base


class DownloadedFile(Base):
    __tablename__ = "downloaded_files"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, nullable=False, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # video/audio/subtitle/thumbnail
    file_size = Column(Integer, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "job_id": self.job_id,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "file_size": self.file_size,
        }
