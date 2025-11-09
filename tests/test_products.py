from typing import Any

from fastapi.testclient import TestClient

from app.models.product import Product


def test_list_products(client: TestClient, test_product: Product):
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == test_product.name


def test_get_product(client: TestClient, test_product: Product):
    response = client.get(f"/api/v1/products/{test_product.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_product.name


def test_get_nonexistent_product(client: TestClient):
    response = client.get("/api/v1/products/9999")
    assert response.status_code == 404


def test_create_product_as_admin(client: TestClient, admin_headers: dict[str, Any]):
    response = client.post(
        "/api/v1/products/",
        headers=admin_headers,
        json={
            "name": "New Product",
            "description": "A new product",
            "price": 49.99,
            "stock_quantity": 5,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Product"


def test_create_product_as_user_fails(client: TestClient, auth_headers: dict[str, Any]):
    response = client.post(
        "/api/v1/products/",
        headers=auth_headers,
        json={
            "name": "New Product",
            "description": "A new product",
            "price": 49.99,
            "stock_quantity": 5,
        },
    )
    assert response.status_code == 403


def test_update_product_as_admin(
    client: TestClient, admin_headers: dict[str, Any], test_product: Product
):
    response = client.patch(
        f"/api/v1/products/{test_product.id}",
        headers=admin_headers,
        json={"name": "Updated Product Name", "price": 129.99},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Product Name"
    assert float(data["price"]) == 129.99
    assert data["description"] == test_product.description


def test_update_nonexistent_product(client: TestClient, admin_headers: dict[str, Any]):
    response = client.patch(
        "/api/v1/products/9999", headers=admin_headers, json={"name": "Does Not Exist"}
    )

    assert response.status_code == 404


def test_delete_product_as_admin(
    client: TestClient, admin_headers: dict[str, Any], test_product: Product
):
    response = client.delete(
        f"/api/v1/products/{test_product.id}", headers=admin_headers
    )

    assert response.status_code == 204

    get_response = client.get(f"/api/v1/products/{test_product.id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_product(client: TestClient, admin_headers: dict[str, Any]):
    response = client.delete("/api/v1/products/9999", headers=admin_headers)

    assert response.status_code == 404
