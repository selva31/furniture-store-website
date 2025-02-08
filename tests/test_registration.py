import pytest
from flask import url_for
from app.models import User  # Import User model from your application


def test_registration(client, app):
    """
    Test user registration functionality.
    """
    # Sample user data
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "Test@123",
        "confirm_password": "Test@123",
        "role": "customer",
        "contact": "1234567890",
        "address": "123 Test Street",
        "city": "Test City",
        "dob": "2000-01-01"
    }

    # Send a POST request to the registration route
    response = client.post(url_for("auth.register"), data=user_data, follow_redirects=True)

   
    # Verify that the user was added to the test database
    with app.app_context():
        user = User.query.filter_by(email="testuser@example.com").first()
        