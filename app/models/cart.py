from datetime import datetime, timezone

from sqlmodel import Field, SQLModel  # type: ignore


class Cart(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CartItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    cart_id: int = Field(foreign_key="cart.id", index=True)
    product_id: int = Field(foreign_key="product.id", index=True)
    quantity: int = Field(gt=0)
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
