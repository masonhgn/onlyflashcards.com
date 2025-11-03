from datetime import datetime
from bson import ObjectId
from models.database import Database

class Flashcard:
    def __init__(self, front, back, set_id, _id=None, created_at=None, last_reviewed=None, 
                 difficulty=None, times_reviewed=0):
        self.front = front  # Front side text
        self.back = back    # Back side text
        self.set_id = set_id  # ID of the flashcard set this belongs to
        self._id = _id if _id else ObjectId()
        self.created_at = created_at if created_at else datetime.utcnow()
        self.last_reviewed = last_reviewed
        self.difficulty = difficulty  # e.g., 'easy', 'medium', 'hard'
        self.times_reviewed = times_reviewed
    
    def to_dict(self):
        """Convert flashcard to dictionary for MongoDB storage"""
        return {
            '_id': self._id,
            'front': self.front,
            'back': self.back,
            'set_id': ObjectId(self.set_id) if isinstance(self.set_id, str) else self.set_id,
            'created_at': self.created_at,
            'last_reviewed': self.last_reviewed,
            'difficulty': self.difficulty,
            'times_reviewed': self.times_reviewed
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create Flashcard instance from MongoDB document"""
        return cls(
            front=data['front'],
            back=data['back'],
            set_id=data['set_id'],
            _id=data['_id'],
            created_at=data.get('created_at', datetime.utcnow()),
            last_reviewed=data.get('last_reviewed'),
            difficulty=data.get('difficulty'),
            times_reviewed=data.get('times_reviewed', 0)
        )
    
    def save(self):
        """Save flashcard to database"""
        db = Database()
        return db.flashcards.insert_one(self.to_dict())
    
    def update(self):
        """Update existing flashcard in database"""
        db = Database()
        return db.flashcards.update_one(
            {'_id': self._id},
            {'$set': self.to_dict()}
        )
    
    def delete(self):
        """Delete flashcard from database"""
        db = Database()
        return db.flashcards.delete_one({'_id': self._id})
    
    @classmethod
    def find_by_id(cls, card_id):
        """Find flashcard by ID"""
        db = Database()
        if isinstance(card_id, str):
            card_id = ObjectId(card_id)
        card_data = db.flashcards.find_one({'_id': card_id})
        if card_data:
            return cls.from_dict(card_data)
        return None
    
    @classmethod
    def find_by_set_id(cls, set_id):
        """Find all flashcards in a set"""
        db = Database()
        if isinstance(set_id, str):
            set_id = ObjectId(set_id)
        cards = db.flashcards.find({'set_id': set_id})
        return [cls.from_dict(card) for card in cards]

