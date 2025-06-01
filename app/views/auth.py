from flask import Blueprint, render_template, request, redirect, url_for, session
from app.controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.main'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        
        if AuthController.signup(username, email, password):
            return redirect(url_for('auth.login'))
        return redirect(url_for('auth.signup'))
    
    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        if AuthController.login(username, password):
            return redirect(url_for('main.main'))
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    AuthController.logout()
    return redirect(url_for('auth.login'))