from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort
from flask_login import login_user, logout_user, login_required
from .forms import RegistrationForm, LoginForm
from flask_mail import Message
from .models import User
from . import db, bcrypt, mail


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
            
            if user.role == 'customer':
                return redirect(url_for('main.customer_dashboard'))
            elif user.role == 'delivery':
                return redirect(url_for('main.delivery_dashboard'))
            else:
                return redirect(url_for('main.default_dashboard'))  # Fallback dashboard
            
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

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
