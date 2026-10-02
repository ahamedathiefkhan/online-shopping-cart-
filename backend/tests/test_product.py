"""
Tests for the product catalog, category, search, and filtering module.
"""
import pytest
from app import create_app
from app.extensions import db
from app.modules.product.models import Product, Category


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


def test_list_products_and_search(client):
    # Fetch seed products
    resp = client.get("/api/products")
    assert resp.status_code == 200
    products = resp.json
    assert len(products) > 0

    # Test category fetching
    cat_resp = client.get("/api/products/categories")
    assert cat_resp.status_code == 200
    assert len(cat_resp.json) > 0

    # Search filter
    search_resp = client.get("/api/products?q=Mouse")
    assert search_resp.status_code == 200
    assert any("Mouse" in p["name"] for p in search_resp.json)
