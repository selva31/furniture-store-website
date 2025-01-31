from flask_login import UserMixin
from datetime import date, datetime
from sqlalchemy import ForeignKey, Enum, Column, Integer, String, Float, Date, DateTime, CheckConstraint
from sqlalchemy.orm import relationship

from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    reset_token = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return f"<User {self.username}>"


class RoleApprovalRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    requested_role = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="pending")  # 'pending', 'approved', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref="role_requests")

    def __repr__(self):
        return f"<RoleApprovalRequest {self.id} - {self.requested_role}>"


class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    manufacturer = db.Column(db.String(100), nullable=True)
    country_of_origin = db.Column(db.String(50), nullable=True)
    avg_rating = db.Column(db.Float, nullable=True)
    discount = db.Column(db.Float, default=0.0, nullable=True)
    size = db.Column(db.String(20))  # Ensure this line exists
    colour = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(10), nullable=True)  # New field for gender
    # Change backref name to avoid conflict
    images = db.relationship("ProductImage", backref="product", lazy=True)
    ratings = relationship("Rating", back_populates="product")

    def __repr__(self):
        return f"<Product {self.name}>"


class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)

    def __repr__(self):
        return f"<ProductImage {self.image_url}>"


class Rating(db.Model):
    __tablename__ = "Rating"
    id = Column(Integer, primary_key=True)
    Product_ID = Column(Integer, ForeignKey("product.id"))
    User_ID = Column(Integer, ForeignKey("user.id"))
    rating = Column(Integer, CheckConstraint("(rating >= 1) AND (rating <= 5)", name="check_rating"))

    user = relationship("User")
    product = relationship("Product")


# Cart Table
class Cart(db.Model):
    __tablename__ = "cart"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id", ondelete="CASCADE"), nullable=False)  # Cascade delete
    total_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    product = db.relationship("Product", backref=db.backref("cart_items", passive_deletes=True))

    def __repr__(self):
        return f"<Cart {self.id}>"


class Wishlist(db.Model):
    __tablename__ = "wishlist"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=True)  # Allow NULL for product_id

    product = db.relationship("Product", backref="wishlist_items")

    def __repr__(self):
        return f"<Wishlist {self.id}>"


class OrderedProduct(db.Model):
    __tablename__ = "ordered_product"
    id = db.Column(db.Integer, primary_key=True)
    order_details_id = db.Column(db.Integer, db.ForeignKey("order_details.id"), nullable=False)  # Foreign key to OrderDetails
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order_amount = db.Column(db.Float, nullable=False)  # Individual item total price
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # Added user_id

    order_details = db.relationship("OrderDetails", backref=db.backref("orders", lazy=True))  # Relationship to OrderDetails
    product = db.relationship("Product", backref=db.backref("order_items", passive_deletes=True))

    def __repr__(self):
        return f"<OrderedProduct {self.id}>"


# OrderDetails Table (modified)
class OrderDetails(db.Model):
    __tablename__ = "order_details"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100), nullable=False)
    user_contact = db.Column(db.String(20), nullable=False)
    user_address = db.Column(db.String(200), nullable=False)
    user_city = db.Column(db.String(100), nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    delivery_charges = db.Column(db.Float, nullable=False)
    grand_total = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)
    delivered_date = db.Column(db.DateTime, nullable=True)  # Added Delivered_Date
    user_id = db.Column(db.Integer, db.ForeignKey("user.id",name="u_id"), nullable=False)  # Added user_id
    assigned_delivery_person_id = Column(Integer, ForeignKey("user.id",name="d_id"), nullable=True)

    status_options = Enum("Pending", "Shipped", "Delivered", "Failed")
    status = db.Column(status_options, default="Pending", nullable=False)  # Corrected Enum usage
    user = relationship("User", foreign_keys=[user_id])
    assigned_delivery_person = relationship("User", foreign_keys=[assigned_delivery_person_id])
    products = relationship("Product", secondary="ordered_product", viewonly=True)

    def __repr__(self):
        return f"<OrderDetails {self.id}>"
