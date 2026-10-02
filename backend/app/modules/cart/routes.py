"""
Cart module — Flask routes / blueprint.
Responsibilities: Cart management (Add, Update quantity, Remove, Clear)
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.modules.cart.models import CartItem
from app.modules.product.models import Product

cart_bp = Blueprint("cart", __name__)


@cart_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"module": "cart", "status": "ok"})


@cart_bp.route("", methods=["GET"])
@cart_bp.route("/", methods=["GET"])
@login_required
def get_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    items_data = [item.to_dict() for item in cart_items if item.product]
    
    total_amount = sum(item["total_price"] for item in items_data)
    total_items = sum(item["quantity"] for item in items_data)

    return jsonify({
        "items": items_data,
        "total_amount": round(total_amount, 2),
        "total_items": total_items,
    }), 200


@cart_bp.route("", methods=["POST"])
@cart_bp.route("/", methods=["POST"])
@login_required
def add_to_cart():
    data = request.get_json() or {}
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    if not product_id or quantity <= 0:
        return jsonify({"error": "Valid product_id and quantity > 0 are required"}), 400

    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    if product.stock_quantity < quantity:
        return jsonify({"error": f"Only {product.stock_quantity} items available in stock"}), 400

    # Check if item already in user's cart
    cart_item = CartItem.query.filter_by(
        user_id=current_user.id, product_id=product_id
    ).first()

    if cart_item:
        new_quantity = cart_item.quantity + quantity
        if product.stock_quantity < new_quantity:
            return jsonify({"error": f"Cannot add more. Stock limit is {product.stock_quantity}"}), 400
        cart_item.quantity = new_quantity
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({
        "message": "Item added to cart",
        "cart_item": cart_item.to_dict()
    }), 201


@cart_bp.route("/<int:item_id>", methods=["PUT"])
@login_required
def update_cart_item(item_id):
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not cart_item:
        return jsonify({"error": "Cart item not found"}), 404

    data = request.get_json() or {}
    quantity = int(data.get("quantity", 1))

    if quantity <= 0:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({"message": "Item removed from cart"}), 200

    if cart_item.product and cart_item.product.stock_quantity < quantity:
        return jsonify({"error": f"Only {cart_item.product.stock_quantity} items available in stock"}), 400

    cart_item.quantity = quantity
    db.session.commit()

    return jsonify({
        "message": "Cart updated",
        "cart_item": cart_item.to_dict()
    }), 200


@cart_bp.route("/<int:item_id>", methods=["DELETE"])
@login_required
def remove_cart_item(item_id):
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not cart_item:
        return jsonify({"error": "Cart item not found"}), 404

    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({"message": "Item removed from cart"}), 200


@cart_bp.route("/clear", methods=["DELETE"])
@login_required
def clear_cart():
    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({"message": "Cart cleared successfully"}), 200
