# from flask import url_for
# from flask_testing import TestCase
# import pytest
# from app import create_app, db
# from app.models import User
# from datetime import date

# @pytest.fixture
# def app():
#     """Create a Flask application instance for testing."""
#     app = create_app()
#     app.config.update({
#         "TESTING": True,
#         "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # Use in-memory SQLite for testing
#         "WTF_CSRF_ENABLED": False,  # Disable CSRF for easier form testing
#     })

#     # Set up the database
#     with app.app_context():
#         db.create_all()
#         yield app
#         db.session.remove()
#         db.drop_all()

# @pytest.fixture
# def client(app):
#     """Provide a test client for the app."""
#     return app.test_client()

# @pytest.fixture
# def runner(app):
#     """Provide a test CLI runner for the app."""
#     return app.test_cli_runner()

# @pytest.fixture
# def create_user(app):
#     """Create a user in the database for testing."""
#     with app.app_context():
#         user = User(
#             username='testuser',
#             email='testuser@example.com',
#             password='hashedpassword',  # Use bcrypt to hash in actual application
#             role='customer',
#             contact='1234567890',
#             location='Test City',
#             dob=date(2000, 1, 1),
#             gender='male'
#         )
#         user.set_password('password123')  # Assuming you have a set_password method
#         db.session.add(user)
#         db.session.commit()
#         return user


# def test_login_invalid_email(client):
#     """Test login with an invalid email."""
#     response = client.post(
#         url_for('auth.login'),
#         data={
#             'email': 'invalid@example.com',  # Email does not exist
#             'password': 'password123'
#         },
#         follow_redirects=True
#     )
#     assert response.status_code == 200
#     assert b'Invalid email or password!' in response.data







import sys
import os
# Add app path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import url_for
from flask_testing import TestCase
import pytest
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
from flask_bcrypt import Bcrypt

@pytest.fixture
def app():
    """Create a Flask application instance for testing."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # Use in-memory SQLite for testing
        "WTF_CSRF_ENABLED": False,  # Disable CSRF for easier form testing
    })

    # Set up the database
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Provide a test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Provide a test CLI runner for the app."""
    return app.test_cli_runner()
from datetime import datetime
@pytest.fixture
def setup_user(app):
    """Create a test user in the database."""
    with app.app_context():
        user = User(
            username='testuser',
            email='testuser@example.com',
            password=generate_password_hash('password123'),
            role='customer',
            contact='1234567890',
            location='Test City',
            dob=datetime.strptime('2000-01-01', '%Y-%m-%d').date(),
            gender='male'
        )
        db.session.add(user)
        db.session.commit()
        return user

def test_login_success(client, setup_user):
    """Test successful login."""
    response = client.post(
        url_for('auth.login'),
        data={
            'email': 'testuser@example.com',
            'password': 'password123'
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Login successful!' in response.data

def test_login_invalid_email(client):
    """Test login with an invalid email."""
    response = client.post(
        url_for('auth.login'),
        data={
            'email': 'invalid@example.com',
            'password': 'password123'
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Invalid email or password!' in response.data

def test_login_incorrect_password(client, setup_user):
    """Test login with an incorrect password."""
    response = client.post(
        url_for('auth.login'),
        data={
            'email': 'testuser@example.com',
            'password': 'wrongpassword'
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Invalid email or password!' in response.data
