import pytest
from app.models import User, db

def test_change_password(client, app):
    """
    Test the change password functionality without affecting the original application.
    """

    # Create a test user in the database
    with app.app_context():
        user = User(
            username="testuser",
            email="testuser@example.com",
            password="OldPass@123",
            role="Customer",
            contact="1234567890",
            address="Test Address",
            city="Test City",
            dob="2000-01-01"
        )
        db.session.add(user)
       
    # Log in the user first
    response = client.post("/login", data={
        "email": "testuser@example.com",
        "password": "OldPass@123"
    }, follow_redirects=True)
    
    # Simulate change password request
    response = client.post("/change_password", data={
        "old_password": "OldPass@123",
        "new_password": "NewPass@456",
        "confirm_password": "NewPass@456"
    }, follow_redirects=True)

    
    # Verify the password has changed in the database
    with app.app_context():
        updated_user = User.query.filter_by(email="testuser@example.com").first()
        