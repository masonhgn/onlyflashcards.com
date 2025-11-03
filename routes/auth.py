from flask import Blueprint, request, jsonify, session
from models.user import User
from utils.validators import validate_email_format, validate_username, validate_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validate required fields
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    # Validate username format
    is_valid_username, username_error = validate_username(username)
    if not is_valid_username:
        return jsonify({'error': f'Invalid username: {username_error}'}), 400
    
    # Validate password strength
    is_valid_password, password_error = validate_password(password)
    if not is_valid_password:
        return jsonify({'error': f'Invalid password: {password_error}'}), 400
    
    # Validate email format
    is_valid_email, email_result = validate_email_format(email)
    if not is_valid_email:
        return jsonify({'error': f'Invalid email format: {email_result}'}), 400
    
    # Use normalized email (lowercase, etc.)
    email = email_result
    
    # Check if username already exists
    if User.find_by_username(username):
        return jsonify({'error': 'Username already exists'}), 400
    
    # Check if email already exists
    if User.find_by_email(email):
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    user = User(username=username, email=email)
    user.set_password(password)
    
    try:
        user.save()
        # Set session after successful registration
        session['user_id'] = str(user._id)
        session['username'] = user.username
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': str(user._id),
                'username': user.username,
                'email': user.email
            }
        }), 201
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Find user by username or email
    user = User.find_by_username(username)
    if not user:
        user = User.find_by_email(username)  # Allow login with email too
    
    if not user:
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Check password
    if not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Set session
    session['user_id'] = str(user._id)
    session['username'] = user.username
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': str(user._id),
            'username': user.username,
            'email': user.email
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'authenticated': False}), 200
    
    user = User.find_by_id(user_id)
    if not user:
        session.clear()
        return jsonify({'authenticated': False}), 200
    
    return jsonify({
        'authenticated': True,
        'user': {
            'id': str(user._id),
            'username': user.username,
            'email': user.email
        }
    }), 200

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get current user profile"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.find_by_id(user_id)
    if not user:
        session.clear()
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': {
            'id': str(user._id),
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }
    }), 200

