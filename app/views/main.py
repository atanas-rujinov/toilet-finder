from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.toilet import Toilet
from app.controllers.toilet_controller import ToiletController

main_bp = Blueprint('main', __name__)

@main_bp.route('/main')
def main():
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('auth.login'))
    
    toilets = Toilet.query.all()
    return render_template('main.html', toilets=toilets)

@main_bp.route('/add_toilet', methods=['POST'])
def add_toilet():
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('auth.login'))
    
    accessible = 'accessible' in request.form
    has_toilet_paper = 'has_toilet_paper' in request.form
    
    ToiletController.add_toilet(
        request.form['latitude'],
        request.form['longitude'],
        request.form['description'],
        accessible,
        has_toilet_paper,
        request.form['cleanliness']
    )
    
    return redirect(url_for('main.main'))

@main_bp.route('/add_review/<int:toilet_id>', methods=['POST'])
def add_review(toilet_id):
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('auth.login'))
    
    accessible = 'accessible' in request.form
    has_toilet_paper = 'has_toilet_paper' in request.form
    comment = request.form.get('comment', '')
    
    ToiletController.add_review(
        toilet_id,
        accessible,
        has_toilet_paper,
        request.form['cleanliness'],
        comment
    )
    
    return redirect(url_for('main.main'))