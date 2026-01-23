from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

from users import fake_users_db, authenticate_user, pwd_context, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

# =========================
# App
# =========================
app = FastAPI()

# =========================
# Models
# =========================
class LoginModel(BaseModel):
    username: str
    password: str

class RegisterModel(BaseModel):
    username: str
    password: str

class RefreshTokenModel(BaseModel):
    refresh_token: str

# =========================
# OAuth2
# =========================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# =========================
# JWT Helpers
# =========================
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = fake_users_db.get(username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user

# =========================
# Routes
# =========================
@app.get("/")
def root():
    return {"message": "Server is running!"}

# -------------------------
# Register new user
# -------------------------
@app.post("/register")
def register(user: RegisterModel):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = pwd_context.hash(user.password)

    fake_users_db[user.username] = {
        "username": user.username,
        "hashed_password": hashed_password,
        "disabled": False
    }

    return {"message": f"User '{user.username}' registered successfully!"}

# -------------------------
# Login
# -------------------------
@app.post("/login")
def login(data: LoginModel):
    user = authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        data={"sub": user["username"]}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# -------------------------
# Refresh Access Token
# -------------------------
@app.post("/refresh")
def refresh_token(data: RefreshTokenModel):
    try:
        payload = jwt.decode(data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None or username not in fake_users_db:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        new_access_token = create_access_token({"sub": username})
        new_refresh_token = create_refresh_token({"sub": username})

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

# -------------------------
# Protected route
# -------------------------
@app.get("/profile")
def profile(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "message": "Authenticated successfully"
    }
