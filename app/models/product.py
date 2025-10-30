from datetime import datetime, timezone
from decimal import Decimal

from sqlmodel import Field, SQLModel  # type: ignore


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=10, max_length=200, index=True)
    description: str
    price: Decimal = Field(max_digits=10, decimal_places=2, gt=0)
    stock_quantity: int = Field(ge=0)
    image_url: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
