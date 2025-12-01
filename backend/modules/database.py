# modules/database.py - Stub Implementation for Local Testing

import json
from datetime import datetime

class DatabaseManager:
    """Stub database manager for local testing"""
    
    def __init__(self):
        print("✅ Database Manager initialized")
        self.files = {}
        self.users = {}
        self.access_logs = []
    
    def insert_file_record(self, data):
        """Insert file record into database"""
        try:
            record_id = len(self.files) + 1
            data['id'] = record_id
            data['created_at'] = datetime.now().isoformat()
            self.files[record_id] = data
            print(f"✅ File record saved to database (ID: {record_id})")
            return data
        except Exception as e:
            print(f"❌ Database insert error: {str(e)}")
            raise
    
    def get_file_by_access_code(self, access_code):
        """Get file record by access code"""
        try:
            for file_record in self.files.values():
                if file_record.get('access_code') == access_code:
                    print(f"✅ File found in database for access code: {access_code}")
                    return file_record
            print(f"⚠️  No file found for access code: {access_code}")
            return None
        except Exception as e:
            print(f"❌ Database query error: {str(e)}")
            raise
    
    def log_access(self, data):
        """Log file access event"""
        try:
            data['logged_at'] = datetime.now().isoformat()
            self.access_logs.append(data)
            print(f"✅ Access event logged for user: {data['user_id']}")
            return True
        except Exception as e:
            print(f"❌ Access logging error: {str(e)}")
            raise
    
    def insert_user(self, user_id, data):
        """Insert user into database"""
        try:
            self.users[user_id] = data
            print(f"✅ User inserted into database: {user_id}")
            return True
        except Exception as e:
            print(f"❌ User insert error: {str(e)}")
            raise
    
    def get_user(self, user_id):
        """Get user from database"""
        return self.users.get(user_id, {})
    
    def get_user_files(self, user_id):
        """Get all files uploaded by user"""
        return [f for f in self.files.values() if f.get('user_id') == user_id]
    
    def get_access_logs(self, access_code):
        """Get access logs for a file"""
        return [l for l in self.access_logs if l.get('access_code') == access_code]
    
    def get_total_files(self):
        return len(self.files)
    
    def get_total_users(self):
        return len(self.users)
    
    def get_total_access_logs(self):
        return len(self.access_logs)
