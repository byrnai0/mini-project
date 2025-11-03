from datetime import datetime
from bson import ObjectId

class User:
    def __init__(self, db):
        self.collection = db.users
    
    def create_user(self, user_data):
        """
        Create a new user
        user_data = {
            'username': str,
            'email': str,
            'password_hash': str,
            'organization': str,
            'attributes': dict,  # e.g., {'role': 'manager', 'department': 'IT'}
            'bcid': str,  # Blockchain ID (will be set by blockchain team)
        }
        """
        user_data['created_at'] = datetime.utcnow()
        user_data['is_active'] = True
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)
    
    def get_user_by_email(self, email):
        return self.collection.find_one({'email': email})
    
    def get_user_by_id(self, user_id):
        return self.collection.find_one({'_id': ObjectId(user_id)})
    
    def update_user_attributes(self, user_id, attributes):
        return self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'attributes': attributes, 'updated_at': datetime.utcnow()}}
        )
    
    def set_blockchain_id(self, user_id, bcid):
        """Called after blockchain team registers user on-chain"""
        return self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'bcid': bcid}}
        )