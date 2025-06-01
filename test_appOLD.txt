import pytest
from app import app, db, User, Toilet, Review

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # in-memory DB for testing
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing

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
        'password': 'password123'  # Fixed: 8+ characters required
    }, follow_redirects=True)
    assert b'Account created successfully!' in res.data
    
    # Login
    res = client.post('/login', data={
        'username': 'user1',
        'password': 'password123'  # Fixed: matching password
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
    client.post('/signup', data={'username':'user1', 'email':'u1@example.com', 'password':'password123'})  # Fixed password
    client.post('/login', data={'username':'user1', 'password':'password123'})  # Fixed password
    
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
        user.set_password('password123')  # Fixed password
        db.session.add(user)
        db.session.commit()
        
        toilet = Toilet(latitude=1, longitude=2, description='Test toilet', cleanliness=3, accessible=True, has_toilet_paper=False, user_id=user.id)
        db.session.add(toilet)
        db.session.commit()
    
    # Need to be logged in to access API
    client.post('/signup', data={'username':'testuser', 'email':'test@example.com', 'password':'password123'})
    client.post('/login', data={'username':'testuser', 'password':'password123'})
    
    res = client.get('/api/toilets')
    assert res.status_code == 200
    json_data = res.get_json()
    assert 'toilets' in json_data
    assert len(json_data['toilets']) == 1

def test_input_validation(client):
    # Test invalid coordinates
    client.post('/signup', data={'username':'user1', 'email':'u1@example.com', 'password':'password123'})
    client.post('/login', data={'username':'user1', 'password':'password123'})
    
    # Invalid latitude
    res = client.post('/add_toilet', data={
        'latitude': 100,  # Invalid: > 90
        'longitude': 20,
        'description': 'Test toilet',
        'cleanliness': 4
    }, follow_redirects=True)
    assert b'Invalid input' in res.data
    
    # Invalid cleanliness rating
    res = client.post('/add_toilet', data={
        'latitude': 10,
        'longitude': 20,
        'description': 'Test toilet',
        'cleanliness': 6  # Invalid: > 5
    }, follow_redirects=True)
    assert b'Invalid input' in res.data

def test_signup_validation(client):
    # Test invalid username (too short)
    res = client.post('/signup', data={
        'username': 'ab',  # Too short
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert b'Username must be 3-20 characters' in res.data
    
    # Test invalid email
    res = client.post('/signup', data={
        'username': 'validuser',
        'email': 'invalid-email',  # Invalid format
        'password': 'password123'
    }, follow_redirects=True)
    assert b'Please enter a valid email address' in res.data
    
    # Test duplicate username
    client.post('/signup', data={'username':'user1', 'email':'u1@example.com', 'password':'password123'})
    res = client.post('/signup', data={
        'username': 'user1',  # Duplicate
        'email': 'different@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert b'Username already exists' in res.data

def test_add_review(client):
    # Setup: create user and toilet
    with app.app_context():
        user = User(username='u', email='u@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        toilet = Toilet(latitude=1, longitude=2, description='Test toilet', cleanliness=3, accessible=True, has_toilet_paper=False, user_id=user.id)
        db.session.add(toilet)
        db.session.commit()
        toilet_id = toilet.id
    
    # Login as different user
    client.post('/signup', data={'username':'reviewer', 'email':'reviewer@example.com', 'password':'password123'})
    client.post('/login', data={'username':'reviewer', 'password':'password123'})
    
    # Add review
    res = client.post(f'/add_review/{toilet_id}', data={
        'cleanliness': 5,
        'accessible': 'on',
        'has_toilet_paper': 'on',
        'comment': 'Great toilet!'
    }, follow_redirects=True)
    assert b'Review submitted successfully!' in res.data

def test_api_toilet_details(client):
    # Setup: create user and toilet with review
    with app.app_context():
        user = User(username='u', email='u@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        toilet = Toilet(latitude=1, longitude=2, description='Test toilet', cleanliness=3, accessible=True, has_toilet_paper=False, user_id=user.id)
        db.session.add(toilet)
        db.session.commit()
        
        review = Review(cleanliness=5, accessible=False, has_toilet_paper=True, comment='Good toilet', user_id=user.id, toilet_id=toilet.id)
        db.session.add(review)
        db.session.commit()
        toilet_id = toilet.id
    
    # Login to access API
    client.post('/signup', data={'username':'testuser', 'email':'test@example.com', 'password':'password123'})
    client.post('/login', data={'username':'testuser', 'password':'password123'})
    
    res = client.get(f'/api/toilet/{toilet_id}')
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data['id'] == toilet_id
    assert len(json_data['reviews']) == 1
    assert json_data['cleanliness'] == 4  # Median of [3, 5]