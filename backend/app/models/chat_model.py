from sqlalchemy import Column, DateTime, Integer, String, func

from app.db.database import Base


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
