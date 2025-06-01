from flask import session, jsonify
from app.models.toilet import Toilet
from app.models.user import User

class ApiController:
    @staticmethod
    def get_toilets():
        if 'user_id' not in session:
            return {"error": "Authentication required"}, 401
            
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
        
        return {'toilets': toilet_list}, 200
    
    @staticmethod
    def get_toilet_details(toilet_id):
        if 'user_id' not in session:
            return {"error": "Authentication required"}, 401

        toilet = Toilet.query.get_or_404(toilet_id)
        user = User.query.get(toilet.user_id)
        author_name = user.username if user else "Unknown"

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

        return toilet_data, 200