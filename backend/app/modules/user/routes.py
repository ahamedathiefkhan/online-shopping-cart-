"""
User module — Flask routes / blueprint.
Responsibilities: Mobile OTP auth, Registration, Profile Management
"""
import random
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.modules.user.models import User

user_bp = Blueprint("user", __name__)


def clean_phone(phone_str):
    if not phone_str:
        return ""
    # Retain digits only
    digits = "".join([c for c in str(phone_str) if c.isdigit()])
    return digits


@user_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"module": "user", "status": "ok"})


@user_bp.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.get_json() or {}
    raw_phone = data.get("phone", "").strip()
    phone = clean_phone(raw_phone)

    if not phone or len(phone) < 7:
        return jsonify({"error": "A valid mobile phone number is required"}), 400

    # Generate 6-digit OTP code
    otp_code = f"{random.randint(100000, 999999)}"
    expiry = datetime.now(timezone.utc) + timedelta(minutes=10)

    user = User.query.filter_by(phone=phone).first()
    if not user:
        # Check if legacy email matches or create draft record
        email = data.get("email", "").strip().lower() or None
        name = data.get("name", "").strip() or f"User {phone[-4:]}"
        role = data.get("role", "customer").lower()
        if role not in ["customer", "admin"]:
            role = "customer"

        user = User(
            name=name,
            phone=phone,
            email=email,
            role=role,
            otp_code=otp_code,
            otp_expiry=expiry
        )
        db.session.add(user)
    else:
        user.otp_code = otp_code
        user.otp_expiry = expiry

    db.session.commit()

    return jsonify({
        "message": f"OTP sent successfully to {raw_phone}",
        "otp": otp_code,
        "phone": phone
    }), 200


@user_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json() or {}
    raw_phone = data.get("phone", "").strip()
    phone = clean_phone(raw_phone)
    otp = data.get("otp", "").strip()
    name = data.get("name", "").strip()

    if not phone or not otp:
        return jsonify({"error": "Mobile number and OTP code are required"}), 400

    user = User.query.filter_by(phone=phone).first()

    if not user or not user.otp_code or user.otp_code != otp:
        return jsonify({"error": "Invalid or expired OTP code"}), 400

    # Check expiration if set
    if user.otp_expiry:
        # Normalize timezone awareness
        expiry = user.otp_expiry
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expiry:
            return jsonify({"error": "OTP has expired. Please request a new one."}), 400

    # Clear OTP after verification
    user.otp_code = None
    user.otp_expiry = None

    if name and name != user.name:
        user.name = name

    db.session.commit()

    # Log in user with permanent session cookie
    login_user(user, remember=True)

    return jsonify({
        "message": "Mobile verification successful",
        "user": user.to_dict()
    }), 200


@user_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    phone = clean_phone(data.get("phone", ""))
    email = data.get("email", "").strip().lower() or None
    password = data.get("password", "")
    role = data.get("role", "customer").lower()

    if not name or not (phone or email):
        return jsonify({"error": "Name and Mobile number are required"}), 400

    if role not in ["customer", "admin"]:
        role = "customer"

    if phone:
        existing_phone = User.query.filter_by(phone=phone).first()
        if existing_phone:
            return jsonify({"error": "Account with this mobile number already exists"}), 400

    if email:
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({"error": "Account with this email already exists"}), 400

    if not phone:
        phone = f"ph_{random.randint(1000000000, 9999999999)}"

    user = User(name=name, phone=phone, email=email, role=role)
    if password:
        user.set_password(password)

    db.session.add(user)
    db.session.commit()

    login_user(user, remember=True)

    return jsonify({
        "message": "User registered successfully",
        "user": user.to_dict()
    }), 201


@user_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    phone = clean_phone(data.get("phone", ""))
    email = data.get("email", "").strip().lower()
    otp = data.get("otp", "").strip()
    password = data.get("password", "")

    # If OTP provided, verify via OTP
    if phone and otp:
        return verify_otp()

    user = None
    if phone:
        user = User.query.filter_by(phone=phone).first()
    if not user and email:
        user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "User account not found"}), 401

    if password and user.check_password(password):
        login_user(user, remember=True)
        return jsonify({
            "message": "Login successful",
            "user": user.to_dict()
        }), 200

    return jsonify({"error": "Invalid credentials or OTP required"}), 401


@user_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"}), 200


@user_bp.route("/profile", methods=["GET"])
def profile():
    if not current_user.is_authenticated:
        return jsonify({"authenticated": False}), 200
    return jsonify({
        "authenticated": True,
        "user": current_user.to_dict()
    }), 200


@user_bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    phone = clean_phone(data.get("phone", ""))
    password = data.get("password", "")

    if name:
        current_user.name = name
    if phone:
        current_user.phone = phone
    if password:
        current_user.set_password(password)

    db.session.commit()
    return jsonify({
        "message": "Profile updated successfully",
        "user": current_user.to_dict()
    }), 200

