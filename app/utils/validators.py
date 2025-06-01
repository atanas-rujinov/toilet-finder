import re

def validate_coordinates(lat, lng):
    try:
        lat = float(lat)
        lng = float(lng)
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            raise ValueError("Invalid coordinates")
        return lat, lng
    except (ValueError, TypeError):
        raise ValueError("Invalid coordinate format")

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    # Only allow alphanumeric and underscore, 3-20 chars
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None