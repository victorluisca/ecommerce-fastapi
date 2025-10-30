from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str
    price: Decimal = Field(max_digits=10, decimal_places=2, gt=0)
    stock_quantity: int = Field(ge=0)
    image_url: str | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: Decimal
    stock_quantity: int
    image_url: str | None
    created_at: datetime


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    stock_quantity: int | None = None
    image_url: str | None = None
