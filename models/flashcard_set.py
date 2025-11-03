from datetime import datetime
from bson import ObjectId
from models.database import Database
from models.flashcard import Flashcard

class FlashcardSet:
    def __init__(self, title, description=None, user_id=None, _id=None, 
                 created_at=None, updated_at=None, is_public=False):
        self.title = title
        self.description = description or ""
        self.user_id = user_id  # ID of the user who created this set
        self._id = _id if _id else ObjectId()
        self.created_at = created_at if created_at else datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.utcnow()
        self.is_public = is_public
    
    def to_dict(self):
        """Convert flashcard set to dictionary for MongoDB storage"""
        return {
            '_id': self._id,
            'title': self.title,
            'description': self.description,
            'user_id': ObjectId(self.user_id) if self.user_id and isinstance(self.user_id, str) else self.user_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_public': self.is_public
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create FlashcardSet instance from MongoDB document"""
        return cls(
            title=data['title'],
            description=data.get('description', ''),
            user_id=data.get('user_id'),
            _id=data['_id'],
            created_at=data.get('created_at', datetime.utcnow()),
            updated_at=data.get('updated_at', datetime.utcnow()),
            is_public=data.get('is_public', False)
        )
    
    def save(self):
        """Save flashcard set to database"""
        db = Database()
        if self._id in [obj['_id'] for obj in db.flashcard_sets.find({'_id': self._id})]:
            # Update existing
            self.updated_at = datetime.utcnow()
            return db.flashcard_sets.update_one(
                {'_id': self._id},
                {'$set': self.to_dict()}
            )
        else:
            # Insert new
            return db.flashcard_sets.insert_one(self.to_dict())
    
    def update(self):
        """Update existing flashcard set in database"""
        db = Database()
        self.updated_at = datetime.utcnow()
        return db.flashcard_sets.update_one(
            {'_id': self._id},
            {'$set': self.to_dict()}
        )
    
    def delete(self):
        """Delete flashcard set and all its flashcards"""
        db = Database()
        # Delete all flashcards in this set
        if isinstance(self._id, str):
            set_id = ObjectId(self._id)
        else:
            set_id = self._id
        db.flashcards.delete_many({'set_id': set_id})
        # Delete the set
        return db.flashcard_sets.delete_one({'_id': self._id})
    
    def get_flashcards(self):
        """Get all flashcards in this set"""
        return Flashcard.find_by_set_id(self._id)
    
    def add_flashcard(self, front, back):
        """Add a new flashcard to this set"""
        flashcard = Flashcard(front=front, back=back, set_id=self._id)
        flashcard.save()
        self.updated_at = datetime.utcnow()
        self.update()
        return flashcard
    
    @classmethod
    def find_by_id(cls, set_id):
        """Find flashcard set by ID"""
        db = Database()
        if isinstance(set_id, str):
            set_id = ObjectId(set_id)
        set_data = db.flashcard_sets.find_one({'_id': set_id})
        if set_data:
            return cls.from_dict(set_data)
        return None
    
    @classmethod
    def find_by_user_id(cls, user_id):
        """Find all flashcard sets for a user"""
        db = Database()
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        sets = db.flashcard_sets.find({'user_id': user_id})
        return [cls.from_dict(s) for s in sets]
    
    @classmethod
    def find_public_sets(cls, limit=10):
        """Find public flashcard sets"""
        db = Database()
        sets = db.flashcard_sets.find({'is_public': True}).limit(limit)
        return [cls.from_dict(s) for s in sets]
    
    @classmethod
    def search_by_title(cls, query, limit=50):
        """Search flashcard sets by title (case-insensitive, partial match)"""
        db = Database()
        # Case-insensitive regex search
        sets = db.flashcard_sets.find({
            'title': {'$regex': query, '$options': 'i'},
            'is_public': True
        }).limit(limit)
        return [cls.from_dict(s) for s in sets]

