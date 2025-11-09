from typing import Any

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.product import Product


def test_add_item_to_cart(
    client: TestClient, auth_headers: dict[str, Any], test_product: Product
):
    response = client.post(
        "/api/v1/cart/items",
        headers=auth_headers,
        json={"product_id": test_product.id, "quantity": 2},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2


def test_add_item_exceeds_stock(
    client: TestClient, auth_headers: dict[str, Any], test_product: Product
):
    response = client.post(
        "/api/v1/cart/items",
        headers=auth_headers,
        json={
            "product_id": test_product.id,
            "quantity": 999,
        },
    )
    assert response.status_code == 400
    assert "stock" in response.json()["detail"].lower()


def test_add_nonexistent_product(client: TestClient, auth_headers: dict[str, Any]):
    response = client.post(
        "/api/v1/cart/items",
        headers=auth_headers,
        json={"product_id": 999, "quantity": 1},
    )
    assert response.status_code == 404
    assert "Product not found" in response.json()["detail"]


def test_update_item_quantity(
    client: TestClient, auth_headers: dict[str, Any], test_product: Product
):
    add_response = client.post(
        "/api/v1/cart/items",
        headers=auth_headers,
        json={"product_id": test_product.id, "quantity": 2},
    )
    cart_item_id = add_response.json()["items"][0]["id"]

    response = client.patch(
        f"/api/v1/cart/items/{cart_item_id}", headers=auth_headers, json={"quantity": 5}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["items"][0]["quantity"] == 5


def test_update_cart_item_exceeds_stock(
    client: TestClient, auth_headers: dict[str, Any], test_product: Product
):
    add_response = client.post(
        "/api/v1/cart/items",
        headers=auth_headers,
        json={"product_id": test_product.id, "quantity": 2},
    )
    cart_item_id = add_response.json()["items"][0]["id"]

    response = client.patch(
        f"/api/v1/cart/items/{cart_item_id}",
        headers=auth_headers,
        json={"quantity": 999},
    )

    assert response.status_code == 400
    assert "stock" in response.json()["detail"].lower()


def test_update_nonexistent_cart_item(client: TestClient, auth_headers: dict[str, Any]):
    response = client.patch(
        "/api/v1/cart/items/9999", headers=auth_headers, json={"quantity": 5}
    )

    assert response.status_code == 404


def test_remove_cart_item(
    client: TestClient, auth_headers: dict[str, Any], test_product: Product
):
    add_response = client.post(
        "/api/v1/cart/items",
        headers=auth_headers,
        json={"product_id": test_product.id, "quantity": 2},
    )
    cart_item_id = add_response.json()["items"][0]["id"]

    response = client.delete(f"/api/v1/cart/items/{cart_item_id}", headers=auth_headers)

    assert response.status_code == 204

    cart_response = client.get("/api/v1/cart/", headers=auth_headers)
    assert len(cart_response.json()["items"]) == 0


def test_clear_cart(
    client: TestClient,
    auth_headers: dict[str, Any],
    test_product: Product,
    session: Session,
):
    from decimal import Decimal

    product2 = Product(
        name="Product 2",
        description="Another product",
        price=Decimal("49.99"),
        stock_quantity=5,
    )
    session.add(product2)
    session.commit()
    session.refresh(product2)

    client.post(
        "/api/v1/cart/items",
        headers=auth_headers,
        json={"product_id": test_product.id, "quantity": 2},
    )
    client.post(
        "/api/v1/cart/items",
        headers=auth_headers,
        json={"product_id": product2.id, "quantity": 1},
    )

    response = client.delete("/api/v1/cart", headers=auth_headers)

    assert response.status_code == 204

    cart_response = client.get("/api/v1/cart/", headers=auth_headers)
    assert len(cart_response.json()["items"]) == 0
