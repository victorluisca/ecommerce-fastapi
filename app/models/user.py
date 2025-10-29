from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel  # type: ignore


class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    full_name: str
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.CUSTOMER)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
