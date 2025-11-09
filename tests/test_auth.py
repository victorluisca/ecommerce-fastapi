from fastapi.testclient import TestClient

from app.models.user import User


def test_register_user(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "User",
            "email": "user@example.com",
            "password": "UserPass123!",
        },
    )
    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "user@example.com"
    assert data["full_name"] == "User"


def test_register_duplicate_email(client: TestClient, test_user: User):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test",
            "email": test_user.email,
            "password": "TestPass123!",
        },
    )
    assert response.status_code == 409
    assert "Email already registered" in response.json()["detail"]


def test_login_success(client: TestClient, test_user: User):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": "TestPass123!"},
    )
    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient, test_user: User):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": "WrongPassword"},
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "nobody@example.com", "password": "Password123!"},
    )
    assert response.status_code == 401
