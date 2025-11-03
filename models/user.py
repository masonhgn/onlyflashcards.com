from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import Database

class User:
    def __init__(self, username, email, password_hash=None, _id=None, created_at=None):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self._id = _id if _id else ObjectId()
        self.created_at = created_at if created_at else datetime.utcnow()
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary for MongoDB storage"""
        return {
            '_id': self._id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create User instance from MongoDB document"""
        return cls(
            username=data['username'],
            email=data['email'],
            password_hash=data.get('password_hash'),
            _id=data['_id'],
            created_at=data.get('created_at', datetime.utcnow())
        )
    
    def save(self):
        """Save user to database"""
        db = Database()
        return db.users.insert_one(self.to_dict())
    
    @classmethod
    def find_by_username(cls, username):
        """Find user by username"""
        db = Database()
        user_data = db.users.find_one({'username': username})
        if user_data:
            return cls.from_dict(user_data)
        return None
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        db = Database()
        user_data = db.users.find_one({'email': email})
        if user_data:
            return cls.from_dict(user_data)
        return None
    
    @classmethod
    def find_by_id(cls, user_id):
        """Find user by ID"""
        db = Database()
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        user_data = db.users.find_one({'_id': user_id})
        if user_data:
            return cls.from_dict(user_data)
        return None

