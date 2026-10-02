"""
Tests for order placement and order history.
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


def test_order_placement(client):
    # Add product to cart
    client.post("/api/cart", json={"product_id": 1, "quantity": 1})

    # Place order
    order_resp = client.post("/api/orders", json={
        "shipping_address": "123 Test St, San Francisco, CA 94105"
    })
    assert order_resp.status_code == 201
    assert order_resp.json["order"]["status"] == "pending"

    # Verify cart cleared
    cart_resp = client.get("/api/cart")
    assert cart_resp.json["total_items"] == 0

    # Verify order appears in order history
    history_resp = client.get("/api/orders")
    assert history_resp.status_code == 200
    assert len(history_resp.json) >= 1
