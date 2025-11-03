from flask import Blueprint, request, jsonify
from models.flashcard_set import FlashcardSet
from models.flashcard import Flashcard
from utils.auth import login_required

cards_bp = Blueprint('cards', __name__)

@cards_bp.route('/set/<set_id>', methods=['POST'])
@login_required
def create_flashcard(set_id, current_user):
    """Add a flashcard to a set (only owner can add)"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    front = data.get('front')
    back = data.get('back')
    
    if not front or not back:
        return jsonify({'error': 'Both front and back are required'}), 400
    
    try:
        # Get the flashcard set
        flashcard_set = FlashcardSet.find_by_id(set_id)
        
        if not flashcard_set:
            return jsonify({'error': 'Flashcard set not found'}), 404
        
        # Check ownership
        if str(flashcard_set.user_id) != str(current_user._id):
            return jsonify({'error': 'You can only add flashcards to your own sets'}), 403
        
        # Add flashcard to set
        flashcard = flashcard_set.add_flashcard(front=front, back=back)
        
        return jsonify({
            'message': 'Flashcard added successfully',
            'flashcard': {
                'id': str(flashcard._id),
                'front': flashcard.front,
                'back': flashcard.back,
                'set_id': str(flashcard.set_id),
                'created_at': flashcard.created_at.isoformat() if flashcard.created_at else None
            }
        }), 201
    except Exception as e:
        return jsonify({'error': f'Failed to create flashcard: {str(e)}'}), 500

@cards_bp.route('/set/<set_id>', methods=['GET'])
def get_flashcards(set_id):
    """Get all flashcards in a set"""
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
        
        flashcards = flashcard_set.get_flashcards()
        
        return jsonify({
            'flashcards': [{
                'id': str(c._id),
                'front': c.front,
                'back': c.back,
                'set_id': str(c.set_id),
                'difficulty': c.difficulty,
                'times_reviewed': c.times_reviewed,
                'last_reviewed': c.last_reviewed.isoformat() if c.last_reviewed else None,
                'created_at': c.created_at.isoformat() if c.created_at else None
            } for c in flashcards]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get flashcards: {str(e)}'}), 500

@cards_bp.route('/<card_id>', methods=['GET'])
def get_flashcard(card_id):
    """Get a specific flashcard by ID"""
    try:
        flashcard = Flashcard.find_by_id(card_id)
        
        if not flashcard:
            return jsonify({'error': 'Flashcard not found'}), 404
        
        # Get the set to check access
        flashcard_set = FlashcardSet.find_by_id(str(flashcard.set_id))
        if not flashcard_set:
            return jsonify({'error': 'Flashcard set not found'}), 404
        
        # Check if user has access (owner or public)
        from flask import session
        current_user_id = session.get('user_id')
        
        is_owner = current_user_id and str(flashcard_set.user_id) == current_user_id
        if not flashcard_set.is_public and not is_owner:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'flashcard': {
                'id': str(flashcard._id),
                'front': flashcard.front,
                'back': flashcard.back,
                'set_id': str(flashcard.set_id),
                'difficulty': flashcard.difficulty,
                'times_reviewed': flashcard.times_reviewed,
                'last_reviewed': flashcard.last_reviewed.isoformat() if flashcard.last_reviewed else None,
                'created_at': flashcard.created_at.isoformat() if flashcard.created_at else None
            }
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get flashcard: {str(e)}'}), 500

@cards_bp.route('/<card_id>', methods=['PUT'])
@login_required
def update_flashcard(card_id, current_user):
    """Update a flashcard (only owner of the set can update)"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        flashcard = Flashcard.find_by_id(card_id)
        
        if not flashcard:
            return jsonify({'error': 'Flashcard not found'}), 404
        
        # Get the set to check ownership
        flashcard_set = FlashcardSet.find_by_id(str(flashcard.set_id))
        if not flashcard_set:
            return jsonify({'error': 'Flashcard set not found'}), 404
        
        # Check ownership
        if str(flashcard_set.user_id) != str(current_user._id):
            return jsonify({'error': 'You can only update flashcards in your own sets'}), 403
        
        # Update fields
        if 'front' in data:
            flashcard.front = data['front']
        if 'back' in data:
            flashcard.back = data['back']
        if 'difficulty' in data:
            flashcard.difficulty = data['difficulty']
        
        flashcard.update()
        
        return jsonify({
            'message': 'Flashcard updated successfully',
            'flashcard': {
                'id': str(flashcard._id),
                'front': flashcard.front,
                'back': flashcard.back,
                'set_id': str(flashcard.set_id),
                'difficulty': flashcard.difficulty,
                'times_reviewed': flashcard.times_reviewed
            }
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to update flashcard: {str(e)}'}), 500

@cards_bp.route('/<card_id>', methods=['DELETE'])
@login_required
def delete_flashcard(card_id, current_user):
    """Delete a flashcard (only owner of the set can delete)"""
    try:
        flashcard = Flashcard.find_by_id(card_id)
        
        if not flashcard:
            return jsonify({'error': 'Flashcard not found'}), 404
        
        # Get the set to check ownership
        flashcard_set = FlashcardSet.find_by_id(str(flashcard.set_id))
        if not flashcard_set:
            return jsonify({'error': 'Flashcard set not found'}), 404
        
        # Check ownership
        if str(flashcard_set.user_id) != str(current_user._id):
            return jsonify({'error': 'You can only delete flashcards from your own sets'}), 403
        
        flashcard.delete()
        
        # Update set's updated_at timestamp
        flashcard_set.updated_at = flashcard_set.updated_at
        flashcard_set.update()
        
        return jsonify({'message': 'Flashcard deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to delete flashcard: {str(e)}'}), 500

