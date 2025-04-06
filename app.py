# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///toilets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    toilets = db.relationship('Toilet', backref='author', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Toilet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    accessible = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists')
            return redirect(url_for('signup'))
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered')
            return redirect(url_for('signup'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully!')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully!')
            return redirect(url_for('main'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Logged out successfully!')
    return redirect(url_for('login'))

@app.route('/main')
def main():
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('login'))
    
    toilets = Toilet.query.all()
    return render_template('main.html', toilets=toilets)

@app.route('/add_toilet', methods=['POST'])
def add_toilet():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    description = request.form['description']
    accessible = 'accessible' in request.form
    
    toilet = Toilet(
        latitude=latitude,
        longitude=longitude,
        description=description,
        accessible=accessible,
        user_id=session['user_id']
    )
    
    db.session.add(toilet)
    db.session.commit()
    
    flash('Toilet added successfully!')
    return redirect(url_for('main'))

@app.route('/api/toilets')
def get_toilets():
    toilets = Toilet.query.all()
    toilet_list = []
    
    for toilet in toilets:
        toilet_data = {
            'id': toilet.id,
            'latitude': toilet.latitude,
            'longitude': toilet.longitude,
            'description': toilet.description,
            'accessible': toilet.accessible,
            'author': User.query.get(toilet.user_id).username
        }
        toilet_list.append(toilet_data)
    
    return {'toilets': toilet_list}

if __name__ == '__main__':
    app.run(debug=True)