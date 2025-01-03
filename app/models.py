from flask_login import UserMixin
from datetime import date, datetime

from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    reset_token = db.Column(db.String(128), nullable=True)
 
    
    def __repr__(self):
        return f'<User {self.username}>'
    
class RoleApprovalRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    requested_role = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='role_requests')

    def __repr__(self):
        return f'<RoleApprovalRequest {self.id} - {self.requested_role}>'
    
class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Max length for string fields
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))  # Optional length
    category = db.Column(db.String(50))
    image_url = db.Column(db.String(255))
    size = db.Column(db.String(20))
    colour = db.Column(db.String(20))
    quantity = db.Column(db.Integer, nullable=False)
    manufacturer = db.Column(db.String(100))
    country_of_origin = db.Column(db.String(100))
    rating = db.Column(db.Float, nullable=True)
    discount = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f'<Product {self.name}>'