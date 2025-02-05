import pytest
from app.models import User,db

def test_update_details(client, app):
    """
    Test updating user details without affecting the original application.
    """

    # Create a test user in the database
    with app.app_context():
        user = User(
            username="olduser",
            email="olduser@example.com",
            password="Test@123",
            role="Customer",
            contact="1234567890",
            address="Old Address",
            city="Old City",
            dob="2000-01-01"
        )
        db.session.add(user)
        
    # Login as the test user
    client.post("/login", data={"email": "olduser@example.com", "password": "Test@123"})

    # New details to update
    update_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "contact": "9876543210",
        "address": "New Address",
        "city": "New City",
    }

    # Send a POST request to the update details endpoint
    response = client.post("/update_profile", data=update_data, follow_redirects=True)

    

    # Verify that the user details are updated in the test database
    with app.app_context():
        updated_user = User.query.filter_by(email="newuser@example.com").first()
        