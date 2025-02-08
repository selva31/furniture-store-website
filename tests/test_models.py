import pytest
from app.models import User, Product, db
from datetime import date

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
            dob=date(2000, 1, 1)
        )
        db.session.add(user)
       
        yield user
        
        

def test_create_user(test_user):
    """Test user model creation."""
  
def test_create_product(app):
    """Test product model creation."""
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
       

       