from sqlalchemy.orm import declarative_base #type: ignore
from sqlalchemy import Column, Integer, String, DateTime, func #type: ignore

Base = declarative_base()

class MessageLog(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(32), index=True)
    message_text = Column(String(1024))
    message_id = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
