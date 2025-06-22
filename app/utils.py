from flask import redirect, url_for, flash
from functools import wraps
from flask_login import current_user
from flask_login import login_required

def restrict_to_admin():
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role != "admin":
                # Redirect to login or unauthorized access page
                flash("Access denied! Admins only.", "danger")
                return redirect(url_for("main.home"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def restrict_to_deliveryPerson():
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role != "delivery":
                # Redirect to login or unauthorized access page
                flash("Access denied! Delivery Person only.", "danger")
                return redirect(url_for("main.home"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator

import qrcode
import os

def generate_qr_code(product_id, output_folder):
    # Set the base URL directly here since no .env is used
    base_url = "http://127.0.0.1:5000"  # Change this if deploying to production

    # Construct the AR view URL
    ar_url = f"{base_url}/ar_view/{product_id}"
    qr_img = qrcode.make(ar_url)

    # Save QR image in the output folder
    qr_path = os.path.join(output_folder, f"qr_product_{product_id}.png")
    qr_img.save(qr_path)
    return f"qr_product_{product_id}.png"

