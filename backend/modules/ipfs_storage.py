# modules/ipfs_storage.py - Stub Implementation for Local Testing

import json
import base64
import hashlib
from datetime import datetime

class IPFSManager:
    """Stub IPFS manager for local testing"""
    
    def __init__(self):
        print("✅ IPFS Storage Manager initialized")
        self.storage = {}
    
    def add(self, data):
        """Add data to IPFS and return hash"""
        try:
            if isinstance(data, bytes):
                file_hash = hashlib.sha256(data).hexdigest()[:16]
            else:
                file_hash = hashlib.sha256(str(data).encode()).hexdigest()[:16]
            
            self.storage[file_hash] = {
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'size': len(data) if isinstance(data, bytes) else len(str(data))
            }
            print(f"✅ Data stored with IPFS hash: Qm{file_hash}")
            return f"Qm{file_hash}"
        except Exception as e:
            print(f"❌ Error storing in IPFS: {str(e)}")
            raise
    
    def get(self, hash_value):
        """Retrieve data from IPFS"""
        try:
            # Remove 'Qm' prefix if present
            key = hash_value.replace('Qm', '') if hash_value.startswith('Qm') else hash_value
            
            if key in self.storage:
                return self.storage[key]['data']
            else:
                print(f"❌ Hash not found in IPFS: {hash_value}")
                raise Exception(f"IPFS hash not found: {hash_value}")
        except Exception as e:
            print(f"❌ Error retrieving from IPFS: {str(e)}")
            raise
