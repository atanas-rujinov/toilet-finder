from flask import Blueprint, flash, redirect, url_for

errors_bp = Blueprint('errors', __name__)

@errors_bp.app_errorhandler(400)
def bad_request(error):
    if error.description == "The CSRF token is missing.":
        flash('Security token missing. Please try again.')
        return redirect(url_for('main.main'))
    return "Bad Request", 400
