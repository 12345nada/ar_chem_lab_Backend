from pydantic import BaseModel, EmailStr
from enum import Enum


class RegisterModel(BaseModel):
    username: str
    email: EmailStr
    password: str


class VerifyEmailModel(BaseModel):
    email: EmailStr
    code: str


class LoginModel(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenModel(BaseModel):
    refresh_token: str


class ForgotPasswordModel(BaseModel):
    email: EmailStr


class ResetPasswordModel(BaseModel):
    email: EmailStr
    code: str
    new_password: str

class LevelEnumSchema(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    expert = "expert"


class UpdateLevelModel(BaseModel):
    username: str
    level: LevelEnumSchema


class UserDataResponse(BaseModel):
    username: str
    email: EmailStr
    is_verified: bool
    disabled: bool
    level: LevelEnumSchema

    class Config:
        from_attributes = True
