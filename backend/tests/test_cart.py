"""
Tests for shopping cart functionality.
"""
import pytest
from app import create_app
from app.extensions import db


from sqlalchemy.pool import StaticPool


@pytest.fixture
def client():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_ENGINE_OPTIONS": {
            "poolclass": StaticPool,
            "connect_args": {"check_same_thread": False}
        }
    })

    with app.test_client() as client:
        with app.app_context():
            # Login default user
            client.post("/api/users/login", json={
                "email": "user@example.com",
                "password": "password123"
            })
            yield client


def test_cart_operations(client):
    # Get initial cart (empty)
    cart_resp = client.get("/api/cart")
    assert cart_resp.status_code == 200
    assert cart_resp.json["total_items"] == 0

    # Add item to cart
    add_resp = client.post("/api/cart", json={"product_id": 1, "quantity": 2})
    assert add_resp.status_code == 201

    # Check updated cart
    cart_resp = client.get("/api/cart")
    assert cart_resp.status_code == 200
    assert cart_resp.json["total_items"] == 2

    # Clear cart
    clear_resp = client.delete("/api/cart/clear")
    assert clear_resp.status_code == 200

    # Check cart is empty
    cart_resp_empty = client.get("/api/cart")
    assert cart_resp_empty.json["total_items"] == 0
