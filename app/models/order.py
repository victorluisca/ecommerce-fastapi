from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from sqlmodel import Field, SQLModel  # type: ignore


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPING = "shipping"
    DELIVERED = "delivered"


class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    total_price: Decimal = Field(max_digits=10, decimal_places=2, gt=0)
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OrderItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", index=True)
    product_id: int = Field(foreign_key="product.id", index=True)
    quantity: int = Field(gt=0)
    price_at_purchase: Decimal = Field(max_digits=10, decimal_places=2, gt=0)
    subtotal: Decimal = Field(max_digits=10, decimal_places=2, gt=0)
