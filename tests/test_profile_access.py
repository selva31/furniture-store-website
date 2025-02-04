from flask import session
import pytest
from werkzeug.security import generate_password_hash
import sys
import os
from datetime import datetime

# Add the root directory of the project to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User
from flask_login import login_user

@pytest.fixture
def app():
    app = create_app()
    {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///users.db",
        "SECRET_KEY": "testsecretkey",
        "WTF_CSRF_ENABLED": False,  # Disable CSRF for testing
        "SERVER_NAME": "localhost"  # Configure SERVER_NAME for URL building
    }
    with app.app_context():
        db.create_all()
        yield app
        
        

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def init_database(app):
    with app.app_context():
        # Check if user already exists
        user = User.query.filter_by(username='testuser').first()
        if not user:
            user = User(username='testuser', email='test@example.com', role='customer', contact='1234567890', address='123 Test St', city='Test City', dob=datetime.strptime('2000-01-01', '%Y-%m-%d').date())
           
            db.session.add(user)
            
        yield db
        db.session.remove()
        

def test_profile_access(client, init_database):
   
        
    session['user_id'] = User.id

    response = client.get(f'/auth/profile/{User.id}')
    