from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.db.database import Base


class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    source_type = Column(String, nullable=False)   # "document" | "website"
    url_or_filename = Column(String, nullable=False)
    chunks_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
