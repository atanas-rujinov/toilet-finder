from app import db
from datetime import datetime
from statistics import median

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