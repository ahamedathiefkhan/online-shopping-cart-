"""
Tests for the user authentication & profile module.
"""
import pytest
from app import create_app
from app.extensions import db
from app.modules.user.models import User


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


def test_user_registration_and_login(client):
    # Register user with phone number
    reg_resp = client.post("/api/users/register", json={
        "name": "Test User",
        "phone": "9888877777",
        "email": "testuser@example.com",
        "password": "password123",
        "role": "customer"
    })
    assert reg_resp.status_code == 201
    assert reg_resp.json["user"]["phone"] == "9888877777"

    # Duplicate registration should fail
    dup_resp = client.post("/api/users/register", json={
        "name": "Test User 2",
        "phone": "9888877777",
        "password": "password123"
    })
    assert dup_resp.status_code == 400

    # Logout
    client.post("/api/users/logout")

    # Request OTP
    otp_resp = client.post("/api/users/send-otp", json={
        "phone": "9888877777"
    })
    assert otp_resp.status_code == 200
    generated_otp = otp_resp.json["otp"]

    # Verify OTP & Login
    verify_resp = client.post("/api/users/verify-otp", json={
        "phone": "9888877777",
        "otp": generated_otp
    })
    assert verify_resp.status_code == 200
    assert verify_resp.json["message"] == "Mobile verification successful"

    # Check profile
    prof_resp = client.get("/api/users/profile")
    assert prof_resp.status_code == 200
    assert prof_resp.json["authenticated"] is True

