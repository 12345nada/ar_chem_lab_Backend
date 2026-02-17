from pydantic import BaseModel

class LoginModel(BaseModel):
    username: str
    password: str

class RegisterModel(BaseModel):
    username: str
    password: str

class RefreshTokenModel(BaseModel):
    refresh_token: str
