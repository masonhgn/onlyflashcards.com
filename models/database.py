from pymongo import MongoClient
from config import Config

class Database:
    _client = None
    _db = None
    
    def __init__(self):
        if Database._client is None:
            Database._client = MongoClient(Config.MONGODB_URI)
            Database._db = Database._client[Config.DATABASE_NAME]
    
    @property
    def db(self):
        return Database._db
    
    @property
    def users(self):
        return self.db.users
    
    @property
    def flashcard_sets(self):
        return self.db.flashcard_sets
    
    @property
    def flashcards(self):
        return self.db.flashcards

