import pytest
from app import create_app, db
from app.models import User, Product
from flask import url_for

@pytest.fixture
def test_user(app):
    """Fixture to create a test user."""
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
      
        

@pytest.fixture
def test_product(app):
    """Fixture to create a test product."""
    with app.app_context():
        product = Product(
            name="TestProduct",
            price=49.99,
            description="A sample test product",
            category="Electronics",
            quantity=10,
            manufacturer="TestCorp",
            country_of_origin="USA",
            avg_rating=4.5,
            discount=5.0,
            size="M",
            colour="Black",
            gender="Unisex"
        )
        db.session.add(product)
        db.session.commit()
        yield product
        db.session.delete(product)
        db.session.commit()

@pytest.fixture
def client(app):
    """Fixture for test client."""
    return app.test_client()

def test_user_login(client, test_user):
    """Test user login functionality."""
    response = client.post('/login', data={
        'email': 'testuser@example.com',
        'password': 'testpass',
    })
    

def test_add_product(client, test_user, test_product):
    """Test adding a product."""
    response = client.post('/add_product', data={
        'name': 'NewProduct',
        'price': '99.99',
        'description': 'A new test product',
        'category': 'TestCategory',
        'quantity': '5',
        'manufacturer': 'NewCorp',
        'country_of_origin': 'USA',
        'avg_rating': '4.7',
        'discount': '10.0',
        'size': 'L',
        'colour': 'Red',
        'gender': 'Unisex',
    })
    

def test_view_product(client, test_product):
    """Test viewing a product's details."""
    

def test_user_logout(client):
    """Test user logout functionality."""
    response = client.get('/logout')
   
