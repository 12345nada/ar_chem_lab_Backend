from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database.session import Base


class UserLevelHistory(Base):
    __tablename__ = "user_level_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    old_level = Column(String, nullable=True)
    new_level = Column(String, nullable=False)
    changed_at = Column(DateTime, server_default=func.now())