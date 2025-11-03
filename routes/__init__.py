from .auth import auth_bp
from .flashcard_sets import sets_bp
from .flashcards import cards_bp
from .views import views_bp

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(sets_bp, url_prefix='/sets')
    app.register_blueprint(cards_bp, url_prefix='/cards')
    app.register_blueprint(views_bp)

