from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort
from flask_login import login_user, logout_user, login_required,current_user
from .forms import RegistrationForm, LoginForm
from flask_mail import Message
from .models import User
from . import db, bcrypt, mail
import logging
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from flask import current_app


# Setup logger (If not already set in your __init__.py)
logger = logging.getLogger(__name__)
auth = Blueprint('auth', __name__)





@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  # Initialize the registration form
    if form.validate_on_submit():  # Check if form is valid on submit
        try:
            # Check if the email already exists in the database
            if User.query.filter_by(email=form.email.data).first():
                flash('This email is already registered.', 'danger')
                return render_template('register.html', form=form)  # Return form with error

            # Hash the password using bcrypt before saving it to the database
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

            # Create a new User instance with data from the form
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

            flash('Registration successful! You can now log in.', 'success')

            # Optionally log the user in right after registration
            login_user(new_user)  # Automatically log in the new user (optional)

            return redirect(url_for('auth.login'))  # Redirect to the login page after successful registration

        except IntegrityError:
            # Handle any database integrity errors (e.g., duplicates, constraints)
            db.session.rollback()
            flash('A database error occurred. Please try again.', 'danger')

        except Exception as e:
            # Log unexpected errors
            logger.error(f"Error during user registration: {e}")
            db.session.rollback()
            flash('An unexpected error occurred during registration. Please try again.', 'danger')

    else:
        # Flash form validation errors to the user
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.capitalize()}: {error}", 'danger')

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



@auth.route('/confirm_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def confirm_delete(id):
    # Fetch the user to delete
    user = User.query.get(id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('auth.profile', id=current_user.id))  # Redirect to profile
    
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
    return render_template('home.html')




def get_serializer():
    """Create a URLSafeTimedSerializer instance within the app context."""
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
def send_password_change_email(user):
    s = get_serializer()  # Get the serializer within the app context
    token = s.dumps(user.email, salt='password-reset-salt')
    """Send an email notification after the password has been changed."""
    msg = Message('Your password has been successfully changed', sender='chamanyadav38113114@gmail.com', 
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

        user = User.query.get(current_user.id)  # Retrieve the logged-in user by session ID

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





