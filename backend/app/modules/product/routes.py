"""
Product module — Flask routes / blueprint.
Responsibilities: View Products, Search & Filter Products, Product Details
"""
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.modules.product.models import Product, Category

product_bp = Blueprint("product", __name__)


@product_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"module": "product", "status": "ok"})


@product_bp.route("", methods=["GET"])
@product_bp.route("/", methods=["GET"])
def list_products():
    query = Product.query

    # Search term
    search_q = request.args.get("q", "").strip()
    if search_q:
        search_filter = f"%{search_q}%"
        query = query.filter(
            (Product.name.ilike(search_filter)) | (Product.description.ilike(search_filter))
        )

    # Category filter
    category_id = request.args.get("category_id")
    if category_id and category_id.isdigit():
        query = query.filter(Product.category_id == int(category_id))

    # Min price filter
    min_price = request.args.get("min_price")
    if min_price:
        try:
            query = query.filter(Product.price >= float(min_price))
        except ValueError:
            pass

    # Max price filter
    max_price = request.args.get("max_price")
    if max_price:
        try:
            query = query.filter(Product.price <= float(max_price))
        except ValueError:
            pass

    # Sorting
    sort_by = request.args.get("sort", "newest")
    if sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort_by == "name":
        query = query.order_by(Product.name.asc())
    else:
        query = query.order_by(Product.created_at.desc())

    products = query.all()
    return jsonify([p.to_dict() for p in products]), 200


@product_bp.route("/<int:id>", methods=["GET"])
def get_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product.to_dict()), 200


@product_bp.route("/categories", methods=["GET"])
def list_categories():
    categories = Category.query.all()
    return jsonify([c.to_dict() for c in categories]), 200
