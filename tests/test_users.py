from typing import Any

from fastapi.testclient import TestClient

from app.models.user import User


def test_get_my_profile(
    client: TestClient, auth_headers: dict[str, Any], test_user: User
):
    response = client.get("/api/v1/users/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name
    assert data["role"] == "customer"
    assert "hashed_password" not in data


def test_get_profile_without_auth(client: TestClient):
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401


def test_update_profile_success(client: TestClient, auth_headers: dict[str, Any]):
    response = client.patch(
        "/api/v1/users/me",
        headers=auth_headers,
        json={"full_name": "New Name", "email": "new@example.com"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "New Name"
    assert data["email"] == "new@example.com"


def test_update_profile_to_existing_email(
    client: TestClient, auth_headers: dict[str, Any], test_admin: User
):
    response = client.patch(
        "/api/v1/users/me", headers=auth_headers, json={"email": test_admin.email}
    )

    assert response.status_code == 409
    assert "already in use" in response.json()["detail"].lower()


def test_change_password_success(
    client: TestClient, auth_headers: dict[str, Any], test_user: User
):
    response = client.put(
        "/api/v1/users/me/password",
        headers=auth_headers,
        json={
            "current_password": "TestPass123!",
            "new_password": "NewPass123!",
            "confirm_password": "NewPass123!",
        },
    )

    assert response.status_code == 200
    assert "success" in response.json()["message"].lower()

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": "NewPass123!"},
    )
    assert login_response.status_code == 200


def test_change_password_wrong_current(
    client: TestClient, auth_headers: dict[str, Any]
):
    response = client.put(
        "/api/v1/users/me/password",
        headers=auth_headers,
        json={
            "current_password": "WrongPassword",
            "new_password": "NewPass123!",
            "confirm_password": "NewPass123!",
        },
    )

    assert response.status_code == 400
    assert "incorrect" in response.json()["detail"].lower()


def test_change_password_mismatch(client: TestClient, auth_headers: dict[str, Any]):
    response = client.put(
        "/api/v1/users/me/password",
        headers=auth_headers,
        json={
            "current_password": "TestPass123!",
            "new_password": "NewPass123!",
            "confirm_password": "DifferentPass123!",
        },
    )

    assert response.status_code == 422
    assert "do not match" in str(response.json()).lower()
