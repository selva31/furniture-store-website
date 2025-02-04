import pytest
from app import create_app, db
from app.models import User, Product, Rating

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
       
       

def test_add_rating(client):
    user = User(username='testuser', email='test@example.com', password='password')
    product = Product(name='Test Product', price=10.00)
    db.session.add(user)
    db.session.add(product)
   
    rating = Rating()
    db.session.add(rating)
 

   
def test_update_rating(client):
    user = User(username='testuser', email='test@example.com', password='password')
    product = Product(name='Test Product', price=10.00)
    rating = Rating( )
    db.session.add(user)
    db.session.add(product)
    db.session.add(rating)
    
    
   
   
    

def test_delete_rating(client):
    user = User(username='testuser', email='test@example.com', password='password')
    product = Product(name='Test Product', price=10.00)
    rating = Rating( )
    db.session.add(user)
    db.session.add(product)
    db.session.add(rating)
   

    
    
    

  