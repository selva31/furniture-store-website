import pytest
from app.models import User, db

@pytest.fixture
def test_user(app):
    """Create a test user in the test database."""
    with app.app_context():
        user = User(
            username="TestUser",
            email="testuser@example.com",
            password="testpass",
            role="customer",
            contact="1234567890",
            address="Test Street",
            city="Test City",
            dob="2000-01-01"
        )
        db.session.add(user)
       
        yield user
       
      

def test_register(client):
    """Test user registration."""
    response = client.post('/register', data={
        'username': 'NewUser',
        'email': 'newuser@example.com',
        'password': 'newpass',
        'confirm_password': 'newpass',
        'contact': '9876543210',
        'address': 'New Street',
        'city': 'New City',
        'dob': '1995-05-05'
    })
    

def test_login(client, test_user):
    """Test user login with valid credentials."""
    response = client.post('/login', data={
        'email': test_user.email,
        'password': 'testpass'
    })
    

def test_login_invalid_credentials(client):
    """Test login with incorrect credentials."""
    response = client.post('/login', data={
        'email': 'wrong@example.com',
        'password': 'wrongpass'
    })
    

def test_logout(client, test_user):
    """Test user logout."""
    client.post('/login', data={
        'email': test_user.email,
        'password': 'testpass'
    })
    response = client.get('/logout', follow_redirects=True)
   

def test_password_reset(client, test_user):
    """Test password reset request."""
    response = client.post('/reset-password', data={'email': test_user.email})
    

def test_password_change(client, test_user):
    """Test changing password after reset."""
    new_password = "newsecurepassword"
    response = client.post('/change-password', data={
        'email': test_user.email,
        'old_password': 'testpass',
        'new_password': new_password,
        'confirm_password': new_password
    })
    

