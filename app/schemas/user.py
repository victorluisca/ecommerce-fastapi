import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ValidationInfo, field_validator

from app.models.user import UserRole


def validate_password_strength(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if len(password) > 128:
        raise ValueError("Password must be at most 128 characters long")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"[0-9]", password):
        raise ValueError("Password must contain at least one number")
    return password


class UserCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    password: str

    @field_validator("password")
    def check_password(cls, v: str) -> str:
        return validate_password_strength(v)


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: UserRole
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=200)
    email: EmailStr | None = None


class ChangePassword(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    def check_password(cls, v: str) -> str:
        return validate_password_strength(v)

    @field_validator("confirm_password")
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v
