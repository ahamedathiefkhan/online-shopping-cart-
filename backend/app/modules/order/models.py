"""
Order module — database models.
Responsibilities: Order placement and order items tracking
"""
from datetime import datetime, timezone
from app.extensions import db


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    shipping_address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


    user = db.relationship("User")
    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else "Unknown",
            "user_phone": self.user.phone if self.user else "N/A",
            "user_email": self.user.email if self.user else "",
            "total_amount": round(float(self.total_amount), 2),
            "status": self.status,
            "shipping_address": self.shipping_address or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "items": [item.to_dict() for item in self.items],
        }


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)

    product = db.relationship("Product")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else "Deleted Product",
            "product_image": self.product.image_url if self.product else None,
            "quantity": self.quantity,
            "price_at_purchase": round(float(self.price_at_purchase), 2),
            "subtotal": round(float(self.price_at_purchase) * self.quantity, 2),
        }
