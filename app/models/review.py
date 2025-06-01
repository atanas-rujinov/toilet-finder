from app import db
from datetime import datetime

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    accessible = db.Column(db.Boolean, default=False)
    has_toilet_paper = db.Column(db.Boolean, default=False)
    cleanliness = db.Column(db.Integer, default=3)  # 1-5 stars
    comment = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    toilet_id = db.Column(db.Integer, db.ForeignKey('toilet.id'), nullable=False)