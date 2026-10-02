"""
Order module — Flask routes / blueprint.
Responsibilities: Order placement, view order status, view order history
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.modules.order.models import Order, OrderItem
from app.modules.cart.models import CartItem
from app.modules.product.models import Product

order_bp = Blueprint("order", __name__)


@order_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"module": "order", "status": "ok"})


@order_bp.route("", methods=["POST"])
@order_bp.route("/", methods=["POST"])
@login_required
def place_order():
    data = request.get_json() or {}
    shipping_address = data.get("shipping_address", "").strip()

    if not shipping_address:
        return jsonify({"error": "Shipping address is required"}), 400

    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        return jsonify({"error": "Your shopping cart is empty"}), 400

    total_amount = 0.0
    order_items_to_create = []

    for item in cart_items:
        product = db.session.get(Product, item.product_id)
        if not product:
            return jsonify({"error": f"Product ID {item.product_id} no longer exists"}), 400
        if product.stock_quantity < item.quantity:
            return jsonify({"error": f"Insufficient stock for '{product.name}'. Only {product.stock_quantity} remaining."}), 400

        item_price = float(product.price)
        total_amount += item_price * item.quantity

        order_items_to_create.append({
            "product": product,
            "quantity": item.quantity,
            "price_at_purchase": item_price
        })

    # Create Order record
    order = Order(
        user_id=current_user.id,
        total_amount=round(total_amount, 2),
        status="pending",
        shipping_address=shipping_address
    )
    db.session.add(order)
    db.session.flush()  # Populate order.id

    # Create OrderItems and decrement stock
    for item_data in order_items_to_create:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data["product"].id,
            quantity=item_data["quantity"],
            price_at_purchase=item_data["price_at_purchase"]
        )
        db.session.add(order_item)
        item_data["product"].stock_quantity -= item_data["quantity"]

    # Clear user cart
    CartItem.query.filter_by(user_id=current_user.id).delete()

    db.session.commit()

    return jsonify({
        "message": "Order placed successfully!",
        "order": order.to_dict()
    }), 201


@order_bp.route("", methods=["GET"])
@order_bp.route("/", methods=["GET"])
@login_required
def get_user_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return jsonify([order.to_dict() for order in orders]), 200


@order_bp.route("/<int:order_id>", methods=["GET"])
@login_required
def get_order_detail(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order.to_dict()), 200
