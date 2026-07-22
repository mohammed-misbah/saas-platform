from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    project_id = Column(Integer,ForeignKey("projects.id"),nullable=False)
    uploaded_by = Column(Integer,ForeignKey("users.id"),nullable=False)
    file_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=func.now())