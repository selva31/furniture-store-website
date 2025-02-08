from app.models import User  # Import User model from models.py
from flask_login import login_user, logout_user

def test_logout(client):
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
        
    # Test that the user is logged in
    response = client.get('/profile')  # Example of a protected route
   
    # Log out the user
    response = client.get('/logout')  # Adjust the route as per your app's logout route

    

    # Test that the user is logged out
    response = client.get('/profile')  # Attempt to access a protected route after logging out
   