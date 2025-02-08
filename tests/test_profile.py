from app.models import User  # Import User model from models.py
from flask_login import login_user

def test_profile(client):
    # Create a test user in the in-memory database
    with client.application.app_context():
        user = User(
            username="Test User", 
            email="test@example.com", 
            password="password", 
            role="Customer", 
            contact="1234567890", 
            address="123 Test St", 
            city="Test City", 
            dob="2000-01-01"
        )
       
    # Log in the test user
    with client.application.app_context():
        user = User.query.filter_by(email="test@example.com").first()  # Retrieve user
       
    # Test that the user is logged in and can access the profile page
    response = client.get('/profile')  # Adjust the route to your actual profile route

   