import pytest
from app.models import User, db

def test_delete_user(client, app):
    """
    Test deleting a user without affecting the original application.
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
        user_id = user.id  # Store the user's ID

    # Login as the test user
    client.post("/login", data={"email": "testuser@example.com", "password": "Test@123"})

    # Send a DELETE request to the user deletion endpoint
    response = client.post(f"/delete_user/{user_id}", follow_redirects=True)

    #
    # Verify that the user is removed from the test database
    with app.app_context():
        deleted_user = User.query.filter_by(id=user_id).first()
       
