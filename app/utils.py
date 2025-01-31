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
