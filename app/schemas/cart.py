from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.product import ProductResponse


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
    id: int
    product: ProductResponse
    quantity: int
    subtotal: Decimal
    added_at: datetime


class CartResponse(BaseModel):
    id: int
    user_id: int
    items: list[CartItemResponse]
    total: Decimal
    created_at: datetime
    updated_at: datetime
