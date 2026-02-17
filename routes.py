# routes.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from schemas import LoginModel, RegisterModel, RefreshTokenModel
from security import create_access_token, create_refresh_token, get_current_user, SECRET_KEY, ALGORITHM
from database import get_db
from users_crud import create_user, get_user, authenticate_user
from models_db import User

router = APIRouter()


# ===== Root =====
@router.get("/")
def root():
    return {"message": "Server is running!"}


# ===== Register =====
@router.post("/register")
def register(user: RegisterModel, db: Session = Depends(get_db)):
    """
    تسجّل user جديد في الداتا بيز
    """
    existing_user = get_user(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    create_user(db, user.username, user.password)
    return {"message": f"User '{user.username}' registered successfully!"}


# ===== Login =====
@router.post("/login")
def login(data: LoginModel, db: Session = Depends(get_db)):
    """
    تسجيل دخول + إصدار Access + Refresh Tokens
    """
    user = authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {
        "access_token": create_access_token({"sub": user.username}),
        "refresh_token": create_refresh_token({"sub": user.username}),
        "token_type": "bearer"
    }


# ===== Refresh Token =====
@router.post("/refresh")
def refresh_token(data: RefreshTokenModel, db: Session = Depends(get_db)):
    """
    تحديث Access + Refresh Tokens باستخدام Refresh Token موجود
    """
    try:
        payload = jwt.decode(data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None or not get_user(db, username):
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        return {
            "access_token": create_access_token({"sub": username}),
            "refresh_token": create_refresh_token({"sub": username}),
            "token_type": "bearer"
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


# ===== Profile (Protected Route) =====
@router.get("/profile")
def profile(current_user: User = Depends(get_current_user)):
    """
    صفحة محمية + تعرض بيانات المستخدم
    """
    return {
        "username": current_user.username,
        "message": "Authenticated successfully"
    }
