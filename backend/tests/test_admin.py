"""
Tests for admin dashboard metrics, product management, and order fulfillment.
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
            yield client


def test_admin_access_guard(client):
    # Customer login
    client.post("/api/users/login", json={
        "email": "user@example.com",
        "password": "password123"
    })

    # Customer trying to access admin dashboard should get 403
    forbidden_resp = client.get("/api/admin/dashboard")
    assert forbidden_resp.status_code == 403


def test_admin_crud_and_dashboard(client):
    # Admin login
    client.post("/api/users/login", json={
        "email": "admin@example.com",
        "password": "admin123"
    })

    # Get admin dashboard metrics
    stats_resp = client.get("/api/admin/dashboard")
    assert stats_resp.status_code == 200
    assert "total_products" in stats_resp.json

    # Create new product as admin
    new_prod_resp = client.post("/api/admin/products", json={
        "name": "Admin Test Monitor",
        "description": "4K Ultra HD Display",
        "price": 349.99,
        "stock_quantity": 10,
        "category_id": 1
    })
    assert new_prod_resp.status_code == 201
    prod_id = new_prod_resp.json["product"]["id"]

    # Delete product
    del_resp = client.delete(f"/api/admin/products/{prod_id}")
    assert del_resp.status_code == 200
