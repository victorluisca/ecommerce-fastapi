from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.order import OrderStatus
from app.schemas.product import ProductResponse


class OrderItemResponse(BaseModel):
    id: int
    product: ProductResponse
    quantity: int
    price_at_purchase: Decimal
    subtotal: Decimal


class OrderResponse(BaseModel):
    id: int
    user_id: int
    items: list[OrderItemResponse]
    total_price: Decimal
    status: OrderStatus
    created_at: datetime
    updated_at: datetime


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
