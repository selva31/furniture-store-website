from . import db,bcrypt
from .models import User
from datetime import datetime

def create_customer_user():
    customer = db.session.query(User).filter_by(email="customer@gmail.com").first()
    if not customer:
        hashed_password = bcrypt.generate_password_hash("customer123").decode("utf-8")
        new_customer = User(
            username="customer",
            email="customer@gmail.com",
            password=hashed_password,
            role="customer",
            contact="1234567890",
            address="Street-218, Ahmedabad, Gujarat, India, 38006",
            city="Ahmedabad",
            dob=datetime(1990, 1, 1).date(),
        )
        db.session.add(new_customer)
        db.session.commit()