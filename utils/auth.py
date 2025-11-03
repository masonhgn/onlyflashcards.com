from functools import wraps
from flask import session, jsonify
from models.user import User

def login_required(f):
    """Decorator to require authentication for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        user = User.find_by_id(user_id)
        if not user:
            session.clear()
            return jsonify({'error': 'User not found'}), 401
        
        # Add user to kwargs so routes can access it
        kwargs['current_user'] = user
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current logged in user from session"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    
    return User.find_by_id(user_id)

