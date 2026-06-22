from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.user import User
from app.models.user import User, LevelEnum
from app.models.user_level_history import UserLevelHistory


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, username: str, email: str, password: str):
    user = User(
        username=username,
        email=email,
        hashed_password=pwd_context.hash(password),
        disabled=False,
        is_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def update_password(db: Session, user: User, new_password: str):
    user.hashed_password = pwd_context.hash(new_password)
    db.commit()
    return user

def set_user_level(db: Session, user: User, new_level: str):
    if new_level not in LevelEnum.__members__:
        raise ValueError("Invalid level")

    old_level = user.level
    user.level = new_level

    history = UserLevelHistory(
        user_id=user.id,
        old_level=old_level.value if old_level else None,
        new_level=new_level
    )
    db.add(history)
    db.commit()
    db.refresh(user)
    return user


def get_user_level(db: Session, username: str):
    user = get_user(db, username)
    if not user:
        return None
    return user.level


def search_user_full_data(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()