from flask import session, flash
from app import db
from app.models.toilet import Toilet
from app.models.review import Review
from app.utils.validators import validate_coordinates
from markupsafe import escape

class ToiletController:
    @staticmethod
    def add_toilet(latitude, longitude, description, accessible, has_toilet_paper, cleanliness):
        try:
            # Validate coordinates
            lat, lng = validate_coordinates(latitude, longitude)
            
            # Sanitize and validate description
            desc = escape(description.strip())
            if len(desc) > 200:
                desc = desc[:200]
            if not desc:
                flash('Description is required')
                return False
            
            # Validate cleanliness rating
            clean_rating = int(cleanliness)
            if not (1 <= clean_rating <= 5):
                raise ValueError("Invalid cleanliness rating")
            
            toilet = Toilet(
                latitude=lat,
                longitude=lng,
                description=desc,
                accessible=accessible,
                has_toilet_paper=has_toilet_paper,
                cleanliness=clean_rating,
                user_id=session['user_id']
            )
            
            db.session.add(toilet)
            db.session.commit()
            
            flash('Toilet added successfully!')
            return True
            
        except (ValueError, KeyError) as e:
            flash(f'Invalid input: {str(e)}')
            return False
        except Exception as e:
            flash('An error occurred while adding the toilet')
            return False
    
    @staticmethod
    def add_review(toilet_id, accessible, has_toilet_paper, cleanliness, comment):
        try:
            toilet = Toilet.query.get_or_404(toilet_id)
            
            # Validate cleanliness rating
            clean_rating = int(cleanliness)
            if not (1 <= clean_rating <= 5):
                raise ValueError("Invalid cleanliness rating")
            
            # Sanitize comment
            sanitized_comment = escape(comment.strip())
            if len(sanitized_comment) > 200:
                sanitized_comment = sanitized_comment[:200]
            
            # Create new review
            review = Review(
                accessible=accessible,
                has_toilet_paper=has_toilet_paper,
                cleanliness=clean_rating,
                comment=sanitized_comment,
                user_id=session['user_id'],
                toilet_id=toilet_id
            )
            
            db.session.add(review)
            db.session.commit()
            
            flash('Review submitted successfully!')
            return True
            
        except (ValueError, KeyError) as e:
            flash(f'Invalid input: {str(e)}')
            return False
        except Exception as e:
            flash('An error occurred while submitting the review')
            return False