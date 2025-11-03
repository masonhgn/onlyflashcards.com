from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from models.flashcard_set import FlashcardSet
from models.user import User
from utils.auth import get_current_user

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def home():
    """Home page - search and browse public flashcard sets"""
    current_user = get_current_user()
    
    # Get recent public sets
    recent_sets = FlashcardSet.find_public_sets(limit=12)
    
    return render_template('home.html', 
                         user=current_user,
                         recent_sets=recent_sets)

@views_bp.route('/dashboard')
def dashboard():
    """User dashboard - manage own flashcard sets"""
    current_user = get_current_user()
    
    if not current_user:
        return redirect(url_for('views.login'))
    
    # Get user's flashcard sets
    user_sets = FlashcardSet.find_by_user_id(str(current_user._id))
    
    # Get flashcard count for each set
    set_counts = {}
    for s in user_sets:
        card_count = len(s.get_flashcards())
        set_counts[str(s._id)] = card_count
    
    return render_template('dashboard.html',
                         user=current_user,
                         sets=user_sets,
                         set_counts=set_counts)

@views_bp.route('/login')
def login():
    """Login page"""
    current_user = get_current_user()
    
    if current_user:
        return redirect(url_for('views.dashboard'))
    
    return render_template('login.html')

@views_bp.route('/register')
def register():
    """Registration page"""
    current_user = get_current_user()
    
    if current_user:
        return redirect(url_for('views.dashboard'))
    
    return render_template('register.html')

@views_bp.route('/set/<set_id>')
def view_set(set_id):
    """View a flashcard set"""
    flashcard_set = FlashcardSet.find_by_id(set_id)
    current_user = get_current_user()
    
    if not flashcard_set:
        return render_template('404.html'), 404
    
    # Check access
    is_owner = current_user and str(flashcard_set.user_id) == str(current_user._id)
    if not flashcard_set.is_public and not is_owner:
        return render_template('403.html'), 403
    
    flashcards = flashcard_set.get_flashcards()
    
    return render_template('view_set.html',
                         set=flashcard_set,
                         flashcards=flashcards,
                         user=current_user,
                         is_owner=is_owner)

@views_bp.route('/set/<set_id>/study')
def study_set(set_id):
    """Study a flashcard set"""
    flashcard_set = FlashcardSet.find_by_id(set_id)
    current_user = get_current_user()
    
    if not flashcard_set:
        return render_template('404.html'), 404
    
    # Check access
    is_owner = current_user and str(flashcard_set.user_id) == str(current_user._id)
    if not flashcard_set.is_public and not is_owner:
        return render_template('403.html'), 403
    
    flashcards = flashcard_set.get_flashcards()
    
    if not flashcards:
        return redirect(url_for('views.view_set', set_id=set_id))
    
    # Convert Flashcard objects to dictionaries for JSON serialization
    flashcards_data = [{
        'id': str(card._id),
        'front': card.front,
        'back': card.back,
        'set_id': str(card.set_id)
    } for card in flashcards]
    
    return render_template('study.html',
                         set=flashcard_set,
                         flashcards=flashcards,
                         flashcards_data=flashcards_data,
                         user=current_user,
                         is_owner=is_owner)

