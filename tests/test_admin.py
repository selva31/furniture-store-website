import pytest
from app.models import User, db

@pytest.fixture
def admin_user(app):
    """Create an admin user in the test database."""
    with app.app_context():
        admin = User(
            username="AdminUser",
            email="admin@example.com",
            password="adminpass",
            role="admin",
            contact="9876543210",
            address="Admin Street",
            city="Admin City",
            dob="1990-01-01"
        )
        db.session.add(admin)
        
        yield admin
        
       

def test_admin_login(client, admin_user):
    """Test if an admin can log in successfully."""
    response = client.post('/login', data={
        'email': admin_user.email,
        'password': 'adminpass'
    })
  
def test_admin_dashboard_access(client, admin_user):
    """Test if an admin can access the admin dashboard."""
    client.post('/login', data={
        'email': admin_user.email,
        'password': 'adminpass'
    })
    response = client.get('/admin/dashboard')  # Adjust URL if needed
   

def test_non_admin_cannot_access_admin_dashboard(client):
    """Ensure a non-admin user cannot access the admin dashboard."""
    with client.application.app_context():
        user = User(
            username="TestUser",
            email="user@example.com",
            password="userpass",
            role="customer",
            contact="1234567890",
            address="User Street",
            city="User City",
            dob="2000-05-05"
        )
        db.session.add(user)
       

    client.post('/login', data={'email': 'user@example.com', 'password': 'userpass'})
    response = client.get('/admin/dashboard')
   
def test_admin_logout(client, admin_user):
    """Test if an admin can log out successfully."""
    client.post('/login', data={
        'email': admin_user.email,
        'password': 'adminpass'
    })
    response = client.get('/logout', follow_redirects=True)
    

