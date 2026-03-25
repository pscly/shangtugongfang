from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    workspace_name: str = Field(min_length=2, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenPayload(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
    workspace: dict | None = None
