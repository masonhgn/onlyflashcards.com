from flask import Blueprint, request, jsonify
from bson import ObjectId
from models.flashcard_set import FlashcardSet
from models.flashcard import Flashcard
from utils.auth import login_required

sets_bp = Blueprint('sets', __name__)

@sets_bp.route('', methods=['POST'])
@login_required
def create_set(current_user):
    """Create a new flashcard set"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    title = data.get('title')
    description = data.get('description', '')
    is_public = data.get('is_public', False)
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    # Create flashcard set
    flashcard_set = FlashcardSet(
        title=title,
        description=description,
        user_id=str(current_user._id),
        is_public=is_public
    )
    
    try:
        flashcard_set.save()
        return jsonify({
            'message': 'Flashcard set created successfully',
            'set': {
                'id': str(flashcard_set._id),
                'title': flashcard_set.title,
                'description': flashcard_set.description,
                'user_id': str(flashcard_set.user_id),
                'is_public': flashcard_set.is_public,
                'created_at': flashcard_set.created_at.isoformat() if flashcard_set.created_at else None
            }
        }), 201
    except Exception as e:
        return jsonify({'error': f'Failed to create flashcard set: {str(e)}'}), 500

@sets_bp.route('', methods=['GET'])
def get_sets():
    """Get flashcard sets - user's own sets if authenticated, or public sets"""
    user_id = request.args.get('user_id')  # Optional: get specific user's sets
    public_only = request.args.get('public_only', 'false').lower() == 'true'
    
    # Check if requesting user's own sets
    from flask import session
    current_user_id = session.get('user_id')
    
    if user_id:
        # Get specific user's sets
        sets = FlashcardSet.find_by_user_id(user_id)
        # Only show public sets if not the owner
        if not current_user_id or str(user_id) != current_user_id:
            sets = [s for s in sets if s.is_public]
    elif public_only or not current_user_id:
        # Get public sets only
        limit = int(request.args.get('limit', 50))
        sets = FlashcardSet.find_public_sets(limit=limit)
    else:
        # Get current user's sets
        sets = FlashcardSet.find_by_user_id(current_user_id)
    
    return jsonify({
        'sets': [{
            'id': str(s._id),
            'title': s.title,
            'description': s.description,
            'user_id': str(s.user_id) if s.user_id else None,
            'is_public': s.is_public,
            'created_at': s.created_at.isoformat() if s.created_at else None,
            'updated_at': s.updated_at.isoformat() if s.updated_at else None
        } for s in sets]
    }), 200

@sets_bp.route('/<set_id>', methods=['GET'])
def get_set(set_id):
    """Get a specific flashcard set by ID"""
    try:
        flashcard_set = FlashcardSet.find_by_id(set_id)
        
        if not flashcard_set:
            return jsonify({'error': 'Flashcard set not found'}), 404
        
        # Check if user has access (owner or public)
        from flask import session
        current_user_id = session.get('user_id')
        
        is_owner = current_user_id and str(flashcard_set.user_id) == current_user_id
        if not flashcard_set.is_public and not is_owner:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get flashcards in this set
        flashcards = flashcard_set.get_flashcards()
        
        return jsonify({
            'set': {
                'id': str(flashcard_set._id),
                'title': flashcard_set.title,
                'description': flashcard_set.description,
                'user_id': str(flashcard_set.user_id) if flashcard_set.user_id else None,
                'is_public': flashcard_set.is_public,
                'created_at': flashcard_set.created_at.isoformat() if flashcard_set.created_at else None,
                'updated_at': flashcard_set.updated_at.isoformat() if flashcard_set.updated_at else None,
                'is_owner': is_owner
            },
            'flashcards': [{
                'id': str(c._id),
                'front': c.front,
                'back': c.back,
                'set_id': str(c.set_id),
                'difficulty': c.difficulty,
                'times_reviewed': c.times_reviewed,
                'created_at': c.created_at.isoformat() if c.created_at else None
            } for c in flashcards]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get flashcard set: {str(e)}'}), 500

@sets_bp.route('/<set_id>', methods=['PUT'])
@login_required
def update_set(set_id, current_user):
    """Update a flashcard set (only owner can update)"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        flashcard_set = FlashcardSet.find_by_id(set_id)
        
        if not flashcard_set:
            return jsonify({'error': 'Flashcard set not found'}), 404
        
        # Check ownership
        if str(flashcard_set.user_id) != str(current_user._id):
            return jsonify({'error': 'You can only update your own flashcard sets'}), 403
        
        # Update fields
        if 'title' in data:
            flashcard_set.title = data['title']
        if 'description' in data:
            flashcard_set.description = data['description']
        if 'is_public' in data:
            flashcard_set.is_public = bool(data['is_public'])
        
        flashcard_set.update()
        
        return jsonify({
            'message': 'Flashcard set updated successfully',
            'set': {
                'id': str(flashcard_set._id),
                'title': flashcard_set.title,
                'description': flashcard_set.description,
                'user_id': str(flashcard_set.user_id),
                'is_public': flashcard_set.is_public,
                'updated_at': flashcard_set.updated_at.isoformat() if flashcard_set.updated_at else None
            }
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to update flashcard set: {str(e)}'}), 500

@sets_bp.route('/<set_id>', methods=['DELETE'])
@login_required
def delete_set(set_id, current_user):
    """Delete a flashcard set (only owner can delete)"""
    try:
        flashcard_set = FlashcardSet.find_by_id(set_id)
        
        if not flashcard_set:
            return jsonify({'error': 'Flashcard set not found'}), 404
        
        # Check ownership
        if str(flashcard_set.user_id) != str(current_user._id):
            return jsonify({'error': 'You can only delete your own flashcard sets'}), 403
        
        flashcard_set.delete()
        
        return jsonify({'message': 'Flashcard set deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to delete flashcard set: {str(e)}'}), 500

@sets_bp.route('/my-sets', methods=['GET'])
@login_required
def get_my_sets(current_user):
    """Get current user's flashcard sets"""
    try:
        sets = FlashcardSet.find_by_user_id(str(current_user._id))
        
        return jsonify({
            'sets': [{
                'id': str(s._id),
                'title': s.title,
                'description': s.description,
                'user_id': str(s.user_id),
                'is_public': s.is_public,
                'created_at': s.created_at.isoformat() if s.created_at else None,
                'updated_at': s.updated_at.isoformat() if s.updated_at else None
            } for s in sets]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get flashcard sets: {str(e)}'}), 500

@sets_bp.route('/search', methods=['GET'])
def search_sets():
    """Search flashcard sets by title"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    try:
        from models.user import User
        limit = int(request.args.get('limit', 50))
        sets = FlashcardSet.search_by_title(query, limit=limit)
        
        # Get usernames for each set
        sets_with_usernames = []
        for s in sets:
            username = None
            if s.user_id:
                user = User.find_by_id(str(s.user_id))
                if user:
                    username = user.username
            
            sets_with_usernames.append({
                'id': str(s._id),
                'title': s.title,
                'description': s.description,
                'user_id': str(s.user_id) if s.user_id else None,
                'username': username,
                'is_public': s.is_public,
                'created_at': s.created_at.isoformat() if s.created_at else None
            })
        
        return jsonify({
            'query': query,
            'sets': sets_with_usernames,
            'count': len(sets_with_usernames)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

