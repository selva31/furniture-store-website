import pytest
from app.models import User, db

def test_forgot_password(client, app):
    """
    Test the forgot password functionality without affecting the original application.
    """

    # Create a test user in the database
    with app.app_context():
        user = User(
            username="testuser",
            email="testuser@example.com",
            password="Test@123",
            role="Customer",
            contact="1234567890",
            address="Test Address",
            city="Test City",
            dob="2000-01-01"
        )
        db.session.add(user)
       
    # Simulate forgot password request
    response = client.post("/forgot_password", data={"email": "testuser@example.com"}, follow_redirects=True)

    

    # Check if a reset token is generated in the database
    with app.app_context():
        updated_user = User.query.filter_by(email="testuser@example.com").first()
       
