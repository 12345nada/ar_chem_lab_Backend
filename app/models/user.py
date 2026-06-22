
import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from app.database.session import Base

class LevelEnum(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    expert = "expert"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)
    email = Column(String, unique=True, index=True, nullable=False)
    is_verified = Column(Boolean, default=False)
    otp_code = Column(String, nullable=True)
    otp_expires = Column(DateTime, nullable=True)
    level = Column(Enum(LevelEnum), default=LevelEnum.beginner, nullable=False)