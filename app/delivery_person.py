from flask import request, jsonify, render_template, session, Blueprint, url_for
from flask_mail import Message
from . import db, bcrypt, mail
from .models import OrderDetails, User
from .utils import restrict_to_deliveryPerson
from datetime import datetime
from flask_login import current_user, login_required
from sqlalchemy import and_

delivery_person = Blueprint("delivery_person", __name__, url_prefix="/delivery_person")


# Function to create the delivery person account
def create_delivery_person_user():
    delivery_person = db.session.query(User).filter_by(email="delivery@gmail.com").first()
    if not delivery_person:
        hashed_password = bcrypt.generate_password_hash("delivery123").decode("utf-8")
        new_delivery_person = User(
            username="delivery_person",
            email="delivery@gmail.com",
            password=hashed_password,
            role="delivery",
            contact="1234567890",
            address="Street-218, Ahmedabad, Gujarat, India, 38006",
            city="Ahmedabad",
            dob=datetime(1990, 1, 1).date(),
        )
        db.session.add(new_delivery_person)
        db.session.commit()


# Route to render the dashboard
@delivery_person.route("/")
@login_required
@restrict_to_deliveryPerson()
def delivery_person_dashboard():
    order_status_options = OrderDetails.status_options.enums
    return render_template("delivery_dashboard.html", order_status_options=order_status_options)


# Route to get the orders table for delivery person based on order status
@delivery_person.route("/orders_table")
@login_required
@restrict_to_deliveryPerson()
def filtered_orders_table():
    filtered_order_status = request.args.get("order_status")

    if filtered_order_status not in OrderDetails.status_options.enums:
        return jsonify({"error": "Invalid filter for order status"}), 400

    orders = (
        db.session.query(OrderDetails)
        .filter(
            and_(
                OrderDetails.user.has(city=current_user.city),
                OrderDetails.status == filtered_order_status,
            )
        )
        .all()
    )
    return render_template("delivery_dashboard_orders_table.html", orders=orders)


# Route to update the status of an order
@delivery_person.route("/update_status", methods=["POST"])
@login_required
@restrict_to_deliveryPerson()
def update_status():
    data = request.get_json()
    order_id = data.get("order_id")
    new_status = data.get("status")

    if not order_id or not new_status:
        return jsonify({"error": "Invalid data provided"}), 400

    order = db.session.get(OrderDetails, order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    if new_status not in order.status_options.enums:
        return jsonify({"error": f"Invalid Status For Order"}), 400

    # Update order status
    order.status = new_status
    db.session.commit()

    # Send email if status is changed to "Delivered"
    if new_status == "Delivered":
        order.delivered_date = datetime.now()
        db.session.commit()
        try:
            send_order_delivered_email(order)
        except Exception as e:
            return jsonify({"error": f"Failed to send email: {str(e)}"}), 500
    else:
        order.delivered_date = None
        db.session.commit()

    return jsonify({"message": f"Status updated successfully to {new_status}"}), 200


# Function to send email to the customer
def send_order_delivered_email(order: "OrderDetails"):
    customer_email = order.user.email  # Assuming the `Order` model has a `user` relationship with an `email` attribute
    ratings_link = url_for("rating.rate_order", order_id=order.id, _external=True)

    msg = Message(
        subject="Your Order Has Been Delivered!",
        recipients=[customer_email],
        html=f"""
        <p>Dear {order.user.username},</p>

        <p>Your order has been successfully delivered.</p>
        <p>Please share your feedback by clicking on the link below:</p>
        <p><a href="{ratings_link}">Rate the product</a></p>

        <p>Thank you for shopping with us!</p>
        <p>Best regards,<br>FusionFits</p>
        """,
    )
    try:
        mail.send(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
