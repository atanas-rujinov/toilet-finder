import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///toilets.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False