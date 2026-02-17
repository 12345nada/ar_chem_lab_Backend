# security.py

from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

# لو هتستخدمي DB حقيقي، ممكن تستبدلي fake_users_db بالـ CRUD functions
from users import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    fake_users_db  # ده للـ Fake DB الحالي
)

# ===== OAuth2 Scheme =====
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ===== JWT Helpers =====
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    ينشئ Access Token جديد
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    """
    ينشئ Refresh Token جديد
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ===== Dependency: Get Current User =====
def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    يتحقق من صحة التوكن ويرجع بيانات المستخدم
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # لو مستخدمة Fake DB
    user = fake_users_db.get(username)

    # لو هتستخدمي DB حقيقي بدل fake_users_db، استخدمي:
    # from users_crud import get_user, SessionLocal
    # db = SessionLocal()
    # user = get_user(db, username)

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user
