"""
Admin module — Flask routes / blueprint.
Responsibilities: Product Management, Order Management, Dashboard Metrics
"""
from functools import wraps
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.modules.user.models import User
from app.modules.product.models import Product, Category
from app.modules.order.models import Order

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            return jsonify({"error": "Admin privilege required"}), 403
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"module": "admin", "status": "ok"})


@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def dashboard_stats():
    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()

    completed_orders = Order.query.filter(Order.status != "cancelled").all()
    total_revenue = sum(order.total_amount for order in completed_orders)

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    low_stock = Product.query.filter(Product.stock_quantity <= 5).all()

    return jsonify({
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "total_products": total_products,
        "total_users": total_users,
        "recent_orders": [order.to_dict() for order in recent_orders],
        "low_stock_products": [p.to_dict() for p in low_stock],
    }), 200


@admin_bp.route("/products", methods=["POST"])
@admin_required
def create_product():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    price = data.get("price")
    stock_quantity = data.get("stock_quantity", 0)

    if not name or price is None:
        return jsonify({"error": "Product name and price are required"}), 400

    try:
        price_val = float(price)
        stock_val = int(stock_quantity)
    except ValueError:
        return jsonify({"error": "Price must be a number and stock must be an integer"}), 400

    category_id = data.get("category_id")
    if category_id:
        try:
            category_id = int(category_id)
        except ValueError:
            category_id = None

    product = Product(
        name=name,
        description=data.get("description", "").strip(),
        price=price_val,
        stock_quantity=stock_val,
        category_id=category_id,
        image_url=data.get("image_url", "").strip() or None
    )
    db.session.add(product)
    db.session.commit()

    return jsonify({
        "message": "Product created successfully",
        "product": product.to_dict()
    }), 201


@admin_bp.route("/products/<int:product_id>", methods=["PUT"])
@admin_required
def update_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json() or {}
    if "name" in data:
        product.name = data["name"].strip()
    if "description" in data:
        product.description = data["description"].strip()
    if "price" in data:
        try:
            product.price = float(data["price"])
        except ValueError:
            pass
    if "stock_quantity" in data:
        try:
            product.stock_quantity = int(data["stock_quantity"])
        except ValueError:
            pass
    if "category_id" in data:
        try:
            product.category_id = int(data["category_id"]) if data["category_id"] else None
        except ValueError:
            pass
    if "image_url" in data:
        product.image_url = data["image_url"].strip() or None

    db.session.commit()
    return jsonify({
        "message": "Product updated successfully",
        "product": product.to_dict()
    }), 200


@admin_bp.route("/products/<int:product_id>", methods=["DELETE"])
@admin_required
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 200


@admin_bp.route("/orders", methods=["GET"])
@admin_required
def list_all_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([order.to_dict() for order in orders]), 200


@admin_bp.route("/orders/<int:order_id>/status", methods=["PUT"])
@admin_required
def update_order_status(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    data = request.get_json() or {}
    new_status = data.get("status", "").strip().lower()
    valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]

    if new_status not in valid_statuses:
        return jsonify({"error": f"Invalid status. Must be one of {valid_statuses}"}), 400

    order.status = new_status
    db.session.commit()

    return jsonify({
        "message": "Order status updated",
        "order": order.to_dict()
    }), 200


@admin_bp.route("/categories", methods=["POST"])
@admin_required
def create_category():
    data = request.get_json() or {}
    name = data.get("name", "").strip()

    if not name:
        return jsonify({"error": "Category name is required"}), 400

    existing = Category.query.filter_by(name=name).first()
    if existing:
        return jsonify({"error": "Category already exists"}), 400

    category = Category(name=name)
    db.session.add(category)
    db.session.commit()

    return jsonify({
        "message": "Category created",
        "category": category.to_dict()
    }), 201
