from flask import session, flash
from app import db
from app.models.user import User
from app.utils.validators import validate_username, validate_email

class AuthController:
    @staticmethod
    def signup(username, email, password):
        # Validation
        if not validate_username(username):
            flash('Username must be 3-20 characters, letters/numbers/underscore only')
            return False
            
        if not validate_email(email):
            flash('Please enter a valid email address')
            return False
            
        if len(password) < 8:
            flash('Password must be at least 8 characters long')
            return False
        
        # Check existing users
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return False
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return False
        
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully!')
        return True
    
    @staticmethod
    def login(username, password):
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully!')
            return True
        
        flash('Invalid username or password')
        return False
    
    @staticmethod
    def logout():
        session.pop('user_id', None)
        session.pop('username', None)
        flash('Logged out successfully!')
