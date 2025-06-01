from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flasgger import Swagger
from config import Config

db = SQLAlchemy()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    
    # Swagger setup
    swagger = Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "Toilet Finder API",
            "description": "API documentation for public toilet data",
            "version": "1.0"
        },
        "basePath": "/",
        "schemes": ["http"]
    })
    
    # Register blueprints
    from app.views.auth import auth_bp
    from app.views.main import main_bp
    from app.views.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Error handlers
    from app.views.errors import errors_bp
    app.register_blueprint(errors_bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app