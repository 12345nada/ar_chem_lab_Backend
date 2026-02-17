# database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# هنا بنقول للـ FastAPI "الداتا بيز موجودة في نفس الفولدر"
DATABASE_URL = "sqlite:///./test.db"  # ./ معناها "نفس الفولدر"

# إنشاء المحرك
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# إنشاء Session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# إنشاء Base class لكل الموديلات
Base = declarative_base()

# ===== دالة مساعدة لكل request =====
def get_db():
    """
    دالة تولد Session لكل request
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
