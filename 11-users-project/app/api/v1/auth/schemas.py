from typing import Optional

from core.enums import Role
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class UserPublic(UserBase):
    id: int
    role: Role
    is_active: bool


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    user: UserPublic


class RoleUpdate(BaseModel):
    role: Role


class TokenData(BaseModel):
    sub: str
    username: str
