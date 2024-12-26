from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort
from flask_login import login_user, logout_user, login_required,current_user
from .forms import RegistrationForm, LoginForm
from flask_mail import Message
from .models import User
from . import db, bcrypt, mail
import logging
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash


# Setup logger (If not already set in your __init__.py)
logger = logging.getLogger(__name__)
auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Hash the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # Create a new user instance
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            role=form.role.data,
            contact=form.contact.data,
            location=form.location.data,
            dob=form.dob.data,
            gender=form.gender.data
        )
        
        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('auth.login'))
    print("Form errors:", form.errors)
    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            session['role'] = user.role  # Store the user's role in the session
            session['user_id'] = user.id  # Add user_id to the session
            session['username'] = user.username  # Store the user's username in the session
            # Redirect based on user role
            return render_template('home.html')
            # if user.role == 'customer':
            #     return redirect(url_for('main.customer_dashboard'))
            # elif user.role == 'delivery':
            #     return redirect(url_for('main.delivery_dashboard'))
            # else:
            #     return redirect(url_for('main.default_dashboard'))  # Fallback dashboard
            
        else:
            flash('Invalid email or password!', 'danger')
    return render_template('login.html', form=form)

@auth.route('/profile/<int:id>')
@login_required
def profile(id):
    # Fetch the user with the given ID from the database
    user = User.query.get(id)

    # If the user doesn't exist, return a 404 page
    if not user:
        abort(404)

    # Access control: Allow only the owner or admin
    from flask_login import current_user
    if current_user.id != id and current_user.role != 'admin':
        abort(403)

    # Render the profile.html template with the user's data
    return render_template('profile.html', user=user)

@auth.route('/update_details/<int:id>', methods=['GET', 'POST'])
@login_required
def update_details(id):
    # Fetch the user to update
    user = User.query.get(id)
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
        contact = request.form.get('contact')
        location = request.form.get('location')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        role = request.form.get('role') if current_user.role == 'admin' else user.role  # Only admins can update roles

        # Validate required fields
        if not username or not email:
            flash("Username and Email are required.", "error")
            return redirect(url_for('auth.update_details', id=id))
        
        # Validate and process date of birth
        if dob:
            try:
                dob = datetime.strptime(dob, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid date format. Please use YYYY-MM-DD.", "error")
                return redirect(url_for('auth.update_details', id=id))
        
        # Validate gender
        valid_genders = ['Male', 'Female', 'Other', 'Prefer not to say']
        if gender and gender not in valid_genders:
            flash("Invalid gender selection.", "error")
            return redirect(url_for('auth.update_details', id=id))

        try:
            # Update user details
            user.username = username
            user.email = email
            user.contact = contact
            user.location = location
            user.dob = dob
            user.gender = gender
            user.role = role

            # Commit changes to the database
            db.session.commit()
            flash("User details updated successfully.", "success")
            return redirect(url_for('main.profile'))  # Redirect to an appropriate route
        except Exception as e:
            logger.error(f"Error updating user details for user {id}: {e}")
            db.session.rollback()
            flash("An error occurred while updating the details. Please try again.", "error")
            return redirect(url_for('auth.update_details', id=id))

    # Render the update details form
    return render_template('update_details.html', user=user)



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return render_template('home.html')





