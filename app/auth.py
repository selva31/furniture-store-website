from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort
from flask_login import login_user, logout_user, login_required,current_user
from .forms import RegistrationForm, LoginForm
from .models import User
from . import db, bcrypt, mail
import logging
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from sqlalchemy.exc import IntegrityError
# from app.models import RoleApprovalRequest


# Setup logger (If not already set in your __init__.py)
logger = logging.getLogger(__name__)
auth = Blueprint('auth', __name__)



@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            if User.query.filter_by(email=form.email.data).first():
                flash('This email is already registered.', 'danger')
                return render_template('register.html', form=form)

            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_password,
                role='customer'  # Always default to customer
            )

            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful! You can now log in as a customer.', 'success')
            return redirect(url_for('auth.login'))

        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"IntegrityError during registration: {e}")
            flash('A database error occurred. Please try again.', 'danger')

        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error during registration: {e}")
            flash('An unexpected error occurred during registration. Please try again.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.capitalize()}: {error}", 'danger')

    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # Always safely try to get next and product_id
    next_page = request.args.get('next')
    product_id = request.args.get('product_id')

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            session['role'] = user.role
            session['user_id'] = user.id
            session['username'] = user.username

            # Handle redirect after login
            if next_page:
                if next_page == 'buy_now' and product_id:
                    return redirect(url_for('main.buy_now', product_id=product_id))
                elif next_page == 'add_to_cart' and product_id:
                    return redirect(url_for('main.add_to_cart', product_id=product_id))
                else:
                    return redirect(next_page)

            return redirect(url_for('main.home'))
        else:
            flash('Invalid email or password!', 'danger')

    return render_template('login.html', form=form)

@auth.route('/add_to_cart/<int:product_id>', methods=['GET', 'POST'])
def add_to_cart(product_id):
    if not current_user.is_authenticated:
        next_url = url_for('main.add_to_cart', product_id=product_id)
        return redirect(url_for('auth.login', next=next_url))

    # Your cart logic here...
    flash("Product added to cart!", "success")
    return redirect(url_for('main.cart'))



@auth.route('/profile/<int:id>')
@login_required
def profile(id):
    """
    View function for displaying a user's profile.
    Accessible by the user themselves or an admin.
    """
    # Fetch the user with the given ID or return a 404 if not found
    #user = User.query.get(id)
    user = db.session.get(User, id)
    if not user:
        abort(404)

    # Access control: Only allow the profile owner or an admin
    if current_user.id != id and current_user.role != 'admin':
        abort(403)

    # Render the profile page with the user's data
    return render_template('profile.html', user=user)

@auth.route('/update_details/<int:id>', methods=['GET', 'POST'])
@login_required
def update_details(id):
    # Fetch the user to update
    user = db.session.get(User, id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('main.profile'))  # Redirect to an appropriate route

    # Access control: Only the user or an admin can update details
    if current_user.id != id and current_user.role != 'admin':
        abort(403)

    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role') if current_user.role == 'admin' else user.role  # Only admins can update roles
        # Validate required fields
        if not username or not email:
            flash("Username and Email are required.", "error")
            return redirect(url_for('auth.update_details', id=id))



        # Try to update the user details
        try:
            # Update user details
            user.username = username
            user.email = email
            user.role = role



            # Commit changes to the database
            db.session.commit()

            # Flash success message and redirect to profile page
            flash("User details updated successfully.", "success")
            return redirect(url_for('main.profile'))  # Ensure it redirects here, after success

        except Exception as e:
            logger.error(f"Error updating user details for user {id}: {e}")
            db.session.rollback()  # Rollback in case of error

            # Flash error message and redirect to the same page to try again
            # flash("An error occurred while updating the details. Please try again.", "error")
            return redirect(url_for('auth.update_details', id=id))

    # Render the update details form
    return render_template('update_details.html', user=user)

@auth.route('/confirm_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def confirm_delete(id):
    # Fetch the user to delete
    #user = User.query.get(id)
    user = db.session.get(User, id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('auth.login'))  # Redirect to login page if user not found

    # Access control: Only the user themselves can delete their account
    if current_user.id != id:
        abort(403)

    if request.method == 'POST':
        password = request.form.get('password')

        # Verify the password
        if not bcrypt.check_password_hash(user.password, password):
            flash("Incorrect password. Account deletion canceled.", "error")
            return redirect(url_for('auth.confirm_delete', id=id))

        try:
            # Delete the user from the database
            db.session.delete(user)
            db.session.commit()

            # Log out the user
            logout_user()
            session.clear()

            flash("Your account has been deleted successfully.", "success")
            return render_template('home.html')
        except Exception as e:
            logger.error(f"Error deleting user {id}: {e}")
            db.session.rollback()
            flash("An error occurred while deleting your account. Please try again.", "error")
            return redirect(url_for('auth.confirm_delete', id=id))

    # Render the confirmation page
    return render_template('confirm_delete.html', user=user)




@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))  # Redirect to home




def get_serializer():
    """Create a URLSafeTimedSerializer instance within the app context."""
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
def send_password_change_email(user):
    s = get_serializer()  # Get the serializer within the app context
    token = s.dumps(user.email, salt='password-reset-salt')
    """Send an email notification after the password has been changed."""
    msg = Message('Your password has been successfully changed', sender='selvaqueen333@gmail.com',
                  recipients=[user.email])
    msg.body = f'''Hello {user.username},

Your password has been successfully changed. If you did not make this change, please contact support immediately.

If you have any questions, feel free to reach out to our support team.

Thank you,
Your Application Team
    '''

    try:
        mail.send(msg)  # Attempt to send the email
        print("Password change email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")



@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current-password']
        new_password = request.form['new-password']
        confirm_password = request.form['confirm-password']

        user = db.session.get(User, current_user.id)  # New method using session.get()


        # Verify the current password
        if not bcrypt.check_password_hash(user.password, current_password):
            flash('Current password is incorrect!', 'danger')
            return redirect(url_for('auth.change_password'))

        # Check if new password and confirm password match
        if new_password != confirm_password:
            flash('New password and confirm password do not match!', 'danger')
            return redirect(url_for('auth.change_password'))

        # Update the password in the database
        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()

        flash('Password was successfully changed!', 'success')
        send_password_change_email(user)
        return redirect(url_for('auth.profile', id=current_user.id))  # Redirect to the profile page

    return render_template('change_password.html')

