from passlib.context import CryptContext
from typing import Dict

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Fake DB
fake_users_db: Dict[str, dict] = {
    "nada": {
        "username": "nada",
        "hashed_password": pwd_context.hash("mypassword"),
        "disabled": False
    }
}

# Security Settings
SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Helper Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user
