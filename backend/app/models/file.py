from datetime import datetime
from bson import ObjectId

class File:
    def __init__(self, db):
        self.collection = db.files
    
    def create_file_record(self, file_data):
        """
        file_data = {
            'filename': str,
            'original_filename': str,
            'file_size': int,
            'file_type': str,
            'owner_id': str,
            'ipfs_cid': str,  # Content ID from IPFS
            'encryption_policy': dict,  # ABE access policy
            'encrypted_key': str,  # Encrypted symmetric key
            'blockchain_tx_hash': str,  # Transaction hash (from blockchain team)
            'is_encrypted': bool,
        }
        """
        file_data['created_at'] = datetime.utcnow()
        file_data['access_count'] = 0
        file_data['is_active'] = True
        result = self.collection.insert_one(file_data)
        return str(result.inserted_id)
    
    def get_file_by_id(self, file_id):
        return self.collection.find_one({'_id': ObjectId(file_id)})
    
    def get_files_by_owner(self, owner_id):
        return list(self.collection.find({'owner_id': owner_id, 'is_active': True}))
    
    def get_shared_files(self, user_attributes):
        """Get files where user's attributes match access policy"""
        # This will be complex - we'll implement policy matching logic
        return list(self.collection.find({'is_active': True}))
    
    def increment_access_count(self, file_id):
        return self.collection.update_one(
            {'_id': ObjectId(file_id)},
            {'$inc': {'access_count': 1}}
        )
    
    def update_blockchain_hash(self, file_id, tx_hash):
        """Called after blockchain team stores CID on-chain"""
        return self.collection.update_one(
            {'_id': ObjectId(file_id)},
            {'$set': {'blockchain_tx_hash': tx_hash}}
        )