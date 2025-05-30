import pytest
from app import app, db, User, Toilet, Review

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # in-memory DB for testing

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_user_password():
    u = User(username='test', email='test@example.com')
    u.set_password('secret')
    assert u.check_password('secret')
    assert not u.check_password('wrong')

def test_toilet_median_and_consensus():
    u = User(username='user1', email='u1@example.com')
    u.set_password('pw')
    t = Toilet(latitude=0, longitude=0, cleanliness=3, accessible=True, has_toilet_paper=True, user_id=1)
    
    r1 = Review(cleanliness=5, accessible=True, has_toilet_paper=False)
    r2 = Review(cleanliness=2, accessible=False, has_toilet_paper=True)
    
    t.reviews = [r1, r2]
    
    # Median cleanliness = median([3,5,2]) = 3
    assert t.get_median_cleanliness() == 3
    
    # Accessibility consensus = votes for accessible = 1 (toilet) + 1 (r1) = 2 >= (2+1)/2 = 1.5 -> True
    assert t.get_accessibility_consensus() == True
    
    # Toilet paper consensus = votes = 1 (toilet) + 1 (r2) = 2 >= 1.5 -> True
    assert t.get_toilet_paper_consensus() == True

def test_signup_login_logout(client):
    # Signup
    res = client.post('/signup', data={
        'username': 'user1',
        'email': 'user1@example.com',
        'password': 'pw123'
    }, follow_redirects=True)
    assert b'Account created successfully!' in res.data
    
    # Login
    res = client.post('/login', data={
        'username': 'user1',
        'password': 'pw123'
    }, follow_redirects=True)
    assert b'Logged in successfully!' in res.data
    
    # Logout
    res = client.get('/logout', follow_redirects=True)
    assert b'Logged out successfully!' in res.data

def test_add_toilet_requires_login(client):
    # Without login, redirect to login
    res = client.post('/add_toilet', data={})
    assert res.status_code == 302  # redirect
    
    # Login first
    client.post('/signup', data={'username':'user1', 'email':'u1@example.com', 'password':'pw'})
    client.post('/login', data={'username':'user1', 'password':'pw'})
    
    # Add toilet with minimal data
    res = client.post('/add_toilet', data={
        'latitude': 10,
        'longitude': 20,
        'description': 'Test toilet',
        'cleanliness': 4,
        'accessible': 'on',
        'has_toilet_paper': 'on'
    }, follow_redirects=True)
    assert b'Toilet added successfully!' in res.data

def test_api_toilets(client):
    # Add user and toilet manually
    with app.app_context():
        user = User(username='u', email='u@example.com')
        user.set_password('pw')
        db.session.add(user)
        db.session.commit()
        
        toilet = Toilet(latitude=1, longitude=2, cleanliness=3, accessible=True, has_toilet_paper=False, user_id=user.id)
        db.session.add(toilet)
        db.session.commit()
    
    res = client.get('/api/toilets')
    assert res.status_code == 200
    json_data = res.get_json()
    assert 'toilets' in json_data
    assert len(json_data['toilets']) == 1

