from sqlmodel import Session, SQLModel, create_engine

from app.config import settings
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User

MODELS: list[type[SQLModel]] = [User, Product, Cart, CartItem, Order, OrderItem]

engine = create_engine(
    settings.database_url, connect_args={"check_same_thread": False}, echo=True
)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
