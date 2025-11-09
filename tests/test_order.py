from typing import Any

from fastapi.testclient import TestClient

from app.models.product import Product


def test_create_order_from_cart(
    client: TestClient, auth_headers: dict[str, Any], test_product: Product
):
    client.post(
        "/api/v1/cart/items",
        headers=auth_headers,
        json={"product_id": test_product.id, "quantity": 2},
    )

    response = client.post("/api/v1/orders/", headers=auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2
    assert float(data["total_price"]) > 0


def test_create_order_from_empty_cart(client: TestClient, auth_headers: dict[str, Any]):
    response = client.post("/api/v1/orders/", headers=auth_headers)

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_create_order_clears_cart(
    client: TestClient, auth_headers: dict[str, Any], test_product: Product
):
    client.post(
        "/api/v1/cart/items",
        headers=auth_headers,
        json={"product_id": test_product.id, "quantity": 1},
    )

    client.post("/api/v1/orders/", headers=auth_headers)

    cart_response = client.get("/api/v1/cart/", headers=auth_headers)
    assert len(cart_response.json()["items"]) == 0


def test_create_order_reduces_stock(
    client: TestClient, auth_headers: dict[str, Any], test_product: Product
):
    initial_stock = test_product.stock_quantity

    client.post(
        "/api/v1/cart/items",
        headers=auth_headers,
        json={"product_id": test_product.id, "quantity": 3},
    )

    # Create order
    client.post("/api/v1/orders/", headers=auth_headers)

    product_response = client.get(f"/api/v1/products/{test_product.id}")
    new_stock = product_response.json()["stock_quantity"]
    assert new_stock == initial_stock - 3


def test_create_order_insufficient_stock(
    client: TestClient, auth_headers: dict[str, Any], test_product: Product
):
    response = client.post(
        "/api/v1/cart/items",
        headers=auth_headers,
        json={"product_id": test_product.id, "quantity": 999},
    )

    assert response.status_code == 400


def test_get_my_orders(
    client: TestClient, auth_headers: dict[str, Any], test_product: Product
):
    client.post(
        "/api/v1/cart/items",
        headers=auth_headers,
        json={"product_id": test_product.id, "quantity": 1},
    )
    client.post("/api/v1/orders/", headers=auth_headers)

    response = client.get("/api/v1/orders/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["status"] == "pending"


def test_get_order_by_id(
    client: TestClient, auth_headers: dict[str, Any], test_product: Product
):
    client.post(
        "/api/v1/cart/items",
        headers=auth_headers,
        json={"product_id": test_product.id, "quantity": 2},
    )
    order_response = client.post("/api/v1/orders/", headers=auth_headers)
    order_id = order_response.json()["id"]

    response = client.get(f"/api/v1/orders/{order_id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert len(data["items"]) == 1


def test_get_nonexistent_order(client: TestClient, auth_headers: dict[str, Any]):
    response = client.get("/api/v1/orders/9999", headers=auth_headers)

    assert response.status_code == 404


def test_admin_list_all_orders(
    client: TestClient,
    auth_headers: dict[str, Any],
    admin_headers: dict[str, Any],
    test_product: Product,
):
    client.post(
        "/api/v1/cart/items",
        headers=auth_headers,
        json={"product_id": test_product.id, "quantity": 1},
    )
    client.post("/api/v1/orders/", headers=auth_headers)

    response = client.get("/api/v1/orders/all", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_regular_user_cannot_list_all_orders(
    client: TestClient, auth_headers: dict[str, Any]
):
    response = client.get("/api/v1/orders/all", headers=auth_headers)

    assert response.status_code == 403


def test_admin_update_order_status(
    client: TestClient,
    admin_headers: dict[str, Any],
    auth_headers: dict[str, Any],
    test_product: Product,
):
    client.post(
        "/api/v1/cart/items",
        headers=auth_headers,
        json={"product_id": test_product.id, "quantity": 1},
    )
    order_response = client.post("/api/v1/orders/", headers=auth_headers)
    order_id = order_response.json()["id"]

    response = client.patch(
        f"/api/v1/orders/{order_id}", headers=admin_headers, json={"status": "paid"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "paid"


def test_regular_user_cannot_update_order_status(
    client: TestClient, auth_headers: dict[str, Any], test_product: Product
):
    client.post(
        "/api/v1/cart/items",
        headers=auth_headers,
        json={"product_id": test_product.id, "quantity": 1},
    )
    order_response = client.post("/api/v1/orders/", headers=auth_headers)
    order_id = order_response.json()["id"]

    response = client.patch(
        f"/api/v1/orders/{order_id}", headers=auth_headers, json={"status": "paid"}
    )

    assert response.status_code == 403
