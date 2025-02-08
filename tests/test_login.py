from app.models import db, User
def test_login(client):
    # Create a test user in the database
    from app.models import User
    with client.application.app_context():
        user = User(email="test@example.com", password="password", role="Customer")
        db.session.add(user)
        

    # Valid login
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password',
    })
   

    # Invalid login
    response = client.post('/login', data={
        'email': 'wrong@example.com',
        'password': 'password',
    })