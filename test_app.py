# test_app.py
import unittest
import tempfile
import os
from app import create_app, db
from app.models.user import User
from app.models.toilet import Toilet
from app.models.review import Review
from app.controllers.auth_controller import AuthController
from app.controllers.toilet_controller import ToiletController
from app.controllers.api_controller import ApiController

class FlaskAppTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # Create test app with temporary database
        os.environ['SECRET_KEY'] = 'test_secret_key'
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{self.db_path}"
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up after each test method."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_index_redirect_to_login(self):
        """Test that index redirects to login when not authenticated."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)
    
    def test_signup_page_loads(self):
        """Test that signup page loads successfully."""
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)
    
    def test_login_page_loads(self):
        """Test that login page loads successfully."""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
    
    def test_user_signup_success(self):
        """Test successful user signup."""
        with self.app.test_request_context():
            result = AuthController.signup('testuser', 'test@example.com', 'password123')
            self.assertTrue(result)
            
            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'test@example.com')
    
    def test_user_signup_duplicate_username(self):
        """Test signup with duplicate username fails."""
        with self.app.test_request_context():
            # Create first user
            AuthController.signup('testuser', 'test1@example.com', 'password123')
            
            # Try to create second user with same username
            result = AuthController.signup('testuser', 'test2@example.com', 'password456')
            self.assertFalse(result)
    
    def test_user_signup_duplicate_email(self):
        """Test signup with duplicate email fails."""
        with self.app.test_request_context():
            # Create first user
            AuthController.signup('testuser1', 'test@example.com', 'password123')
            
            # Try to create second user with same email
            result = AuthController.signup('testuser2', 'test@example.com', 'password456')
            self.assertFalse(result)
    
    def test_user_signup_invalid_username(self):
        """Test signup with invalid username fails."""
        with self.app.test_request_context():
            result = AuthController.signup('ab', 'test@example.com', 'password123')  # Too short
            self.assertFalse(result)
    
    def test_user_signup_invalid_email(self):
        """Test signup with invalid email fails."""
        with self.app.test_request_context():
            result = AuthController.signup('testuser', 'invalid-email', 'password123')
            self.assertFalse(result)
    
    def test_user_signup_short_password(self):
        """Test signup with short password fails."""
        with self.app.test_request_context():
            result = AuthController.signup('testuser', 'test@example.com', '123')
            self.assertFalse(result)
    
    def test_user_login_success(self):
        """Test successful user login."""
        with self.app.test_request_context():
            # Create user
            AuthController.signup('testuser', 'test@example.com', 'password123')
            
            # Test login
            result = AuthController.login('testuser', 'password123')
            self.assertTrue(result)
    
    def test_user_login_wrong_password(self):
        """Test login with wrong password fails."""
        with self.app.test_request_context():
            # Create user
            AuthController.signup('testuser', 'test@example.com', 'password123')
            
            # Test login with wrong password
            result = AuthController.login('testuser', 'wrongpassword')
            self.assertFalse(result)
    
    def test_user_login_nonexistent_user(self):
        """Test login with nonexistent user fails."""
        with self.app.test_request_context():
            result = AuthController.login('nonexistent', 'password123')
            self.assertFalse(result)
    
    def test_add_toilet_success(self):
        """Test successful toilet addition."""
        with self.app.test_request_context():
            # Create user and simulate login
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Set session data
            from flask import session
            session['user_id'] = user.id
            session['username'] = user.username
            
            result = ToiletController.add_toilet(
                '42.6977', '23.3219', 'Test toilet', True, True, '4'
            )
            self.assertTrue(result)
            
            toilet = Toilet.query.first()
            self.assertIsNotNone(toilet)
            self.assertEqual(toilet.description, 'Test toilet')
            self.assertEqual(toilet.cleanliness, 4)
    
    def test_add_toilet_invalid_coordinates(self):
        """Test adding toilet with invalid coordinates fails."""
        with self.app.test_request_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            from flask import session
            session['user_id'] = user.id
            
            result = ToiletController.add_toilet(
                '999', '999', 'Test toilet', True, True, '4'  # Invalid coordinates
            )
            self.assertFalse(result)
    
    def test_add_toilet_invalid_cleanliness(self):
        """Test adding toilet with invalid cleanliness rating fails."""
        with self.app.test_request_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            from flask import session
            session['user_id'] = user.id
            
            result = ToiletController.add_toilet(
                '42.6977', '23.3219', 'Test toilet', True, True, '10'  # Invalid rating
            )
            self.assertFalse(result)
    
    def test_add_review_success(self):
        """Test successful review addition."""
        with self.app.test_request_context():
            # Create user and toilet
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            toilet = Toilet(
                latitude=42.6977, longitude=23.3219,
                description='Test toilet', user_id=user.id
            )
            db.session.add(toilet)
            db.session.commit()
            
            from flask import session
            session['user_id'] = user.id
            
            result = ToiletController.add_review(
                toilet.id, True, False, '5', 'Great toilet!'
            )
            self.assertTrue(result)
            
            review = Review.query.first()
            self.assertIsNotNone(review)
            self.assertEqual(review.comment, 'Great toilet!')
            self.assertEqual(review.cleanliness, 5)
    
    def test_toilet_consensus_methods(self):
        """Test toilet consensus calculation methods."""
        with self.app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Create toilet
            toilet = Toilet(
                latitude=42.6977, longitude=23.3219,
                description='Test toilet', accessible=True,
                has_toilet_paper=False, cleanliness=3, user_id=user.id
            )
            db.session.add(toilet)
            db.session.commit()
            
            # Add reviews
            review1 = Review(
                accessible=False, has_toilet_paper=True,
                cleanliness=5, user_id=user.id, toilet_id=toilet.id
            )
            review2 = Review(
                accessible=True, has_toilet_paper=True,
                cleanliness=4, user_id=user.id, toilet_id=toilet.id
            )
            db.session.add(review1)
            db.session.add(review2)
            db.session.commit()
            
            # Test consensus methods
            self.assertTrue(toilet.get_accessibility_consensus())  # 2/3 say accessible
            self.assertTrue(toilet.get_toilet_paper_consensus())   # 2/3 say has paper
            self.assertEqual(toilet.get_median_cleanliness(), 4)   # Median of [3,5,4]
    
    def test_api_get_toilets_unauthorized(self):
        """Test API toilets endpoint without authentication."""
        with self.app.test_request_context():
            data, status = ApiController.get_toilets()
            self.assertEqual(status, 401)
            self.assertIn('error', data)
    
    def test_api_get_toilets_success(self):
        """Test API toilets endpoint with authentication."""
        with self.app.test_request_context():
            # Create user and toilet
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            toilet = Toilet(
                latitude=42.6977, longitude=23.3219,
                description='Test toilet', user_id=user.id
            )
            db.session.add(toilet)
            db.session.commit()
            
            from flask import session
            session['user_id'] = user.id
            
            data, status = ApiController.get_toilets()
            self.assertEqual(status, 200)
            self.assertIn('toilets', data)
            self.assertEqual(len(data['toilets']), 1)
            self.assertEqual(data['toilets'][0]['description'], 'Test toilet')
    
    def test_api_get_toilet_details_success(self):
        """Test API toilet details endpoint."""
        with self.app.test_request_context():
            # Create user and toilet
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            toilet = Toilet(
                latitude=42.6977, longitude=23.3219,
                description='Test toilet', user_id=user.id
            )
            db.session.add(toilet)
            db.session.commit()
            
            from flask import session
            session['user_id'] = user.id
            
            data, status = ApiController.get_toilet_details(toilet.id)
            self.assertEqual(status, 200)
            self.assertEqual(data['description'], 'Test toilet')
            self.assertEqual(data['author'], 'testuser')
    
    def test_main_route_requires_login(self):
        """Test that main route requires authentication."""
        response = self.client.get('/main')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)
    
    def test_signup_form_submission(self):
        """Test signup form submission via HTTP."""
        response = self.client.post('/signup', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful signup
        
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user)
    
    def test_login_form_submission(self):
        """Test login form submission via HTTP."""
        # First create a user
        with self.app.test_request_context():
            AuthController.signup('testuser', 'test@example.com', 'password123')
        
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login

if __name__ == '__main__':
    unittest.main()