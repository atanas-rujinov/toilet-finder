# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from statistics import median

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///toilets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
print("testing autojenkins10")

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    toilets = db.relationship('Toilet', backref='author', lazy=True)
    reviews = db.relationship('Review', backref='author', lazy=True)
    
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
    has_toilet_paper = db.Column(db.Boolean, default=False)
    cleanliness = db.Column(db.Integer, default=3)  # 1-5 stars
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviews = db.relationship('Review', backref='toilet', lazy=True)
    
    def get_median_cleanliness(self):
        all_ratings = [self.cleanliness]  # Include initial rating
        for review in self.reviews:
            all_ratings.append(review.cleanliness)
        return int(median(all_ratings))
    
    def get_accessibility_consensus(self):
        # Count votes for accessibility
        yes_votes = 1 if self.accessible else 0
        for review in self.reviews:
            if review.accessible:
                yes_votes += 1
        
        # If more than half of all reviews (including initial) say it's accessible, consider it accessible
        return yes_votes >= (len(self.reviews) + 1) / 2
    
    def get_toilet_paper_consensus(self):
        # Count votes for toilet paper
        yes_votes = 1 if self.has_toilet_paper else 0
        for review in self.reviews:
            if review.has_toilet_paper:
                yes_votes += 1
        
        # If more than half of all reviews (including initial) say it has toilet paper, consider it has toilet paper
        return yes_votes >= (len(self.reviews) + 1) / 2

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    accessible = db.Column(db.Boolean, default=False)
    has_toilet_paper = db.Column(db.Boolean, default=False)
    cleanliness = db.Column(db.Integer, default=3)  # 1-5 stars
    comment = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    toilet_id = db.Column(db.Integer, db.ForeignKey('toilet.id'), nullable=False)

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
    has_toilet_paper = 'has_toilet_paper' in request.form
    cleanliness = request.form['cleanliness']
    
    toilet = Toilet(
        latitude=latitude,
        longitude=longitude,
        description=description,
        accessible=accessible,
        has_toilet_paper=has_toilet_paper,
        cleanliness=cleanliness,
        user_id=session['user_id']
    )
    
    db.session.add(toilet)
    db.session.commit()
    
    flash('Toilet added successfully!')
    return redirect(url_for('main'))

@app.route('/add_review/<int:toilet_id>', methods=['POST'])
def add_review(toilet_id):
    if 'user_id' not in session:
        return jsonify({"error": "You must be logged in to submit a review"}), 401
    
    toilet = Toilet.query.get_or_404(toilet_id)
    
    # Get review data from form
    accessible = 'accessible' in request.form
    has_toilet_paper = 'has_toilet_paper' in request.form
    cleanliness = int(request.form['cleanliness'])
    comment = request.form.get('comment', '')
    
    # Create new review
    review = Review(
        accessible=accessible,
        has_toilet_paper=has_toilet_paper,
        cleanliness=cleanliness,
        comment=comment,
        user_id=session['user_id'],
        toilet_id=toilet_id
    )
    
    db.session.add(review)
    db.session.commit()
    
    flash('Review submitted successfully!')
    return redirect(url_for('main'))

@app.route('/api/toilets')
def get_toilets():
    toilets = Toilet.query.all()
    toilet_list = []
    
    for toilet in toilets:
        # Find the user
        user = User.query.get(toilet.user_id)
        
        # Set the author name - use username if user exists, otherwise "Unknown"
        author_name = user.username if user else "Unknown"
        
        toilet_data = {
            'id': toilet.id,
            'latitude': toilet.latitude,
            'longitude': toilet.longitude,
            'description': toilet.description,
            'accessible': toilet.get_accessibility_consensus(),
            'has_toilet_paper': toilet.get_toilet_paper_consensus(),
            'cleanliness': toilet.get_median_cleanliness(),
            'review_count': len(toilet.reviews),
            'author': author_name
        }
        toilet_list.append(toilet_data)
    
    return {'toilets': toilet_list}

@app.route('/api/toilet/<int:toilet_id>')
def get_toilet_details(toilet_id):
    toilet = Toilet.query.get_or_404(toilet_id)
    
    # Get user who added the toilet
    user = User.query.get(toilet.user_id)
    author_name = user.username if user else "Unknown"
    
    # Get reviews
    reviews_data = []
    for review in toilet.reviews:
        review_user = User.query.get(review.user_id)
        reviewer_name = review_user.username if review_user else "Unknown"
        
        reviews_data.append({
            'id': review.id,
            'accessible': review.accessible,
            'has_toilet_paper': review.has_toilet_paper,
            'cleanliness': review.cleanliness,
            'comment': review.comment,
            'timestamp': review.timestamp.strftime('%Y-%m-%d %H:%M'),
            'author': reviewer_name
        })
    
    toilet_data = {
        'id': toilet.id,
        'latitude': toilet.latitude,
        'longitude': toilet.longitude,
        'description': toilet.description,
        'accessible': toilet.get_accessibility_consensus(),
        'has_toilet_paper': toilet.get_toilet_paper_consensus(),
        'cleanliness': toilet.get_median_cleanliness(),
        'timestamp': toilet.timestamp.strftime('%Y-%m-%d %H:%M'),
        'author': author_name,
        'reviews': reviews_data
    }
    
    return toilet_data

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
