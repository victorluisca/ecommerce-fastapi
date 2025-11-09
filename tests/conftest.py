from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.security import hash_password
from app.database import get_session
from app.main import app
from app.models.product import Product
from app.models.user import User, UserRole


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    engine.dispose()


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    def get_session_override() -> Generator[Session, None, None]:
        yield session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session) -> User:
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=hash_password("TestPass123!"),
        role=UserRole.CUSTOMER,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="test_admin")
def test_admin_fixture(session: Session) -> User:
    admin = User(
        email="admin@example.com",
        full_name="Admin User",
        hashed_password=hash_password("AdminPass123!"),
        role=UserRole.ADMIN,
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return admin


@pytest.fixture(name="test_product")
def test_product_fixture(session: Session) -> Product:
    from decimal import Decimal

    product = Product(
        name="Test Product",
        description="A test product",
        price=Decimal("99.99"),
        stock_quantity=10,
        image_url="https://example.com/image.jpg",
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client: TestClient, test_user: User) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": "TestPass123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="admin_headers")
def admin_headers_fixture(client: TestClient, test_admin: User) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_admin.email, "password": "AdminPass123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
