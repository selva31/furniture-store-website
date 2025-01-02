from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort
from flask_login import login_user, logout_user, login_required,current_user
from .models import User
from . import db, bcrypt, mail
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from datetime import datetime
from .models import RoleApprovalRequest

admin = Blueprint('admin', __name__)

def create_admin_user():
    admin = User.query.filter_by(email='admin@gmail.com').first()
    if not admin:
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        new_admin = User(
            username='admin',
            email='admin@gmail.com',
            password=hashed_password,
            role='admin',
            contact='1234567890',
            location='Admin Location',
            dob=datetime(1990, 1, 1).date(),
            gender='male'
        )
        db.session.add(new_admin)
        db.session.commit()

@admin.route('/admin/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('admin_dashboard.html', username=session.get('username'))



def send_role_approval_email(user, action, requested_role=None):
    """Send an email notification based on the role approval/rejection."""
    msg_subject = ""
    msg_body = ""

    if action == 'approve':
        msg_subject = 'Your Role Approval Request has been Approved'
        msg_body = f'''Hello {user.username},

Your request to change your role to "{requested_role}" has been approved. You can now access the additional features associated with this role.

If you have any questions, feel free to reach out to our support team.

Thank you,
Your Application Team
        '''
    elif action == 'reject':
        msg_subject = 'Your Role Approval Request has been Rejected'
        msg_body = f'''Hello {user.username},

We regret to inform you that your request to change your role to "{requested_role}" has been rejected. If you believe this is a mistake or have questions, please contact support.

Thank you,
Your Application Team
        '''

    msg = Message(msg_subject, sender='chamanyadav38113114@gmail.com', recipients=[user.email])
    msg.body = msg_body

    try:
        mail.send(msg)  # Attempt to send the email
        print(f"Role approval email ({action}) sent successfully to {user.email}!")
    except Exception as e:
        print(f"Error sending role approval email: {e}")


@admin.route('/admin/role_approval_requests', methods=['GET', 'POST'])
def role_approval_requests():
    if session.get('role') != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('auth.login'))

    # Fetch all pending role approval requests
    requests = RoleApprovalRequest.query.filter_by(status='pending').all()

    if request.method == 'POST':
        request_id = request.form.get('request_id')
        action = request.form.get('action')

        if request_id and action:
            role_request = RoleApprovalRequest.query.get(request_id)
            if role_request:
                user = User.query.get(role_request.user_id)

                if action == 'approve':
                    role_request.status = 'approved'
                    user.role = role_request.requested_role
                    db.session.commit()

                    # Send approval email
                    send_role_approval_email(user, action='approve', requested_role=role_request.requested_role)

                    flash(f"User {user.username}'s role has been updated to {role_request.requested_role}.", 'success')

                elif action == 'reject':
                    role_request.status = 'rejected'
                    db.session.commit()

                    # Send rejection email
                    send_role_approval_email(user, action='reject', requested_role=role_request.requested_role)

                    flash(f"Role request for {user.username} has been rejected.", 'info')

    return render_template('role_approval_requests.html', requests=requests)


@admin.route('/admin/user_details', methods=['GET', 'POST'])
def user_details():
    if session.get('role') != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('auth.login'))

    # Filters
    role_filter = request.args.get('role')
    location_filter = request.args.get('location')
    gender_filter = request.args.get('gender')

    # Query to fetch user details with filters
    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    if location_filter:
        query = query.filter(User.location.ilike(f"%{location_filter}%"))
    if gender_filter:
        query = query.filter_by(gender=gender_filter)

    users = query.all()

    return render_template('user_details.html', users=users, role_filter=role_filter, location_filter=location_filter, gender_filter=gender_filter)


