# users_crud.py

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models_db import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ===== CRUD Functions =====

def get_user(db: Session, username: str):
    """تجيب user من الداتا بيز بالusername"""
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, password: str):
    """تضيف user جديد في الداتا بيز"""
    hashed_password = pwd_context.hash(password)
    user = User(
        username=username,
        hashed_password=hashed_password,
        disabled=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def verify_password(plain_password, hashed_password):
    """يتأكد إن الباسورد صح"""
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    """يتحقق من username + password ويرجع user"""
    user = get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
