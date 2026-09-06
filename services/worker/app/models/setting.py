from sqlalchemy import Column, String
from app.database import Base


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=False)

    def to_dict(self):
        return {
            "key": self.key,
            "value": self.value,
        }
