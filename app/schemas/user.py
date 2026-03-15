from pydantic import BaseModel


class RegisterModel(BaseModel):
    username: str
    email: str
    password: str


class LoginModel(BaseModel):
    #username: str
    email: str
    password: str


class RefreshTokenModel(BaseModel):
    refresh_token: str

class ForgotPasswordModel(BaseModel):
    email: str

class VerifyCodeModel(BaseModel):
    email: str
    code: str


class ResetPasswordModel(BaseModel):
    email: str
    code: str
    new_password: str    