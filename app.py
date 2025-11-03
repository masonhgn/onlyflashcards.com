import os
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from config import Config
from models.database import Database
from routes import register_blueprints

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for frontend integration
CORS(app, supports_credentials=True, origins="*")

# Initialize database connection
db = Database()

# Register blueprints
register_blueprints(app)

# Error handlers - return HTML for browser requests, JSON for API requests
@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/auth/') or request.path.startswith('/sets/') or request.path.startswith('/cards/'):
        return jsonify({'error': 'Route not found'}), 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    if request.path.startswith('/auth/') or request.path.startswith('/sets/') or request.path.startswith('/cards/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500

@app.errorhandler(400)
def bad_request(error):
    if request.path.startswith('/auth/') or request.path.startswith('/sets/') or request.path.startswith('/cards/'):
        return jsonify({'error': 'Bad request'}), 400
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(403)
def forbidden(error):
    if request.path.startswith('/auth/') or request.path.startswith('/sets/') or request.path.startswith('/cards/'):
        return jsonify({'error': 'Forbidden'}), 403
    return render_template('403.html'), 403

@app.errorhandler(401)
def unauthorized(error):
    if request.path.startswith('/auth/') or request.path.startswith('/sets/') or request.path.startswith('/cards/'):
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'error': 'Unauthorized'}), 401

# Health check route
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Server is running'
    }), 200

if __name__ == '__main__':
    # Only run in debug mode if explicitly in development
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=False, host='0.0.0.0', port=5000)
