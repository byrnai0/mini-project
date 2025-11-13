# modules/database.py
import mysql.connector
import json
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        # Get database connection details from environment
        self.config = {
            'host': os.getenv('DATABASE_HOST', 'localhost'),
            'user': os.getenv('DATABASE_USER', 'root'),
            'password': os.getenv('DATABASE_PASSWORD', 'password123'),
            'database': os.getenv('DATABASE_NAME', 'file_sharing_db')
        }
        
        # Connect to MySQL
        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor(dictionary=True)
            print(f"✓ Connected to MySQL at {self.config['host']}")
            
            # Create tables if they don't exist
            self._create_tables()
        except Exception as e:
            raise Exception(f"Failed to connect to database: {str(e)}")
    
    def _create_tables(self):
        """Create necessary database tables"""
        # Users table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                bcid VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                attributes JSON,
                private_key TEXT,
                ethereum_address VARCHAR(255),
                tx_hash VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_bcid (bcid),
                INDEX idx_email (email)
            )
        """)
        
        # Files table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cid VARCHAR(255) UNIQUE NOT NULL,
                owner_bcid VARCHAR(255) NOT NULL,
                filename VARCHAR(255),
                file_size BIGINT,
                access_policy JSON,
                tx_hash VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_bcid) REFERENCES users(bcid),
                INDEX idx_cid (cid),
                INDEX idx_owner (owner_bcid)
            )
        """)
        
        # Access logs table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS access_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cid VARCHAR(255) NOT NULL,
                accessor_bcid VARCHAR(255) NOT NULL,
                access_type VARCHAR(50),
                success BOOLEAN,
                accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_cid (cid),
                INDEX idx_accessor (accessor_bcid)
            )
        """)
        
        self.conn.commit()
        print("✓ Database tables created/verified")
    

    def get_user(self, username):
        """Get user by username"""
        query = "SELECT * FROM users WHERE username = %s"
        result = self.execute_query(query, (username,), fetch=True)
        
        if result:
            user = result[0]
            # Parse attributes from JSON string if needed
            attributes = user.get('attributes')
            if isinstance(attributes, str):
                import json
                attributes = json.loads(attributes)
            
            return {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'bcid': user['bcid'],
                'blockchain_address': user['blockchain_address'],
                'attributes': attributes,
                'private_key': user['private_key'],
                'public_key': user['public_key'],
                'created_at': user['created_at']
            }
        return None

    def insert_user(self, user_data):
        """Insert new user"""
        query = """
            INSERT INTO users (bcid, username, email, attributes, private_key, ethereum_address, tx_hash)
            VALUES (%(bcid)s, %(username)s, %(email)s, %(attributes)s, %(private_key)s, %(ethereum_address)s, %(tx_hash)s)
        """
        self.cursor.execute(query, user_data)
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_user_by_bcid(self, bcid):
        """Get user by BCID"""
        query = "SELECT * FROM users WHERE bcid = %s"
        self.cursor.execute(query, (bcid,))
        return self.cursor.fetchone()
    
    def get_user_by_email(self, email):
        """Get user by email"""
        query = "SELECT * FROM users WHERE email = %s"
        self.cursor.execute(query, (email,))
        return self.cursor.fetchone()
    
    def insert_file(self, file_data):
        """Insert file record"""
        query = """
            INSERT INTO files (cid, owner_bcid, filename, file_size, access_policy, tx_hash)
            VALUES (%(cid)s, %(owner_bcid)s, %(filename)s, %(file_size)s, %(access_policy)s, %(tx_hash)s)
        """
        self.cursor.execute(query, file_data)
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_file_by_cid(self, cid):
        """Get file by CID"""
        query = "SELECT * FROM files WHERE cid = %s"
        self.cursor.execute(query, (cid,))
        return self.cursor.fetchone()
    
    def get_files_by_owner(self, bcid):
        """Get all files owned by user"""
        query = "SELECT * FROM files WHERE owner_bcid = %s ORDER BY created_at DESC"
        self.cursor.execute(query, (bcid,))
        return self.cursor.fetchall()
    
    def get_accessible_files(self, user_attributes):
        """Get files accessible based on user attributes"""
        query = "SELECT * FROM files"
        self.cursor.execute(query)
        all_files = self.cursor.fetchall()
        
        accessible = []
        for file in all_files:
            policy = json.loads(file['access_policy'])
            if self._check_policy_match(user_attributes, policy):
                accessible.append(file)
        
        return accessible
    
    def log_access(self, cid, accessor_bcid, access_type, success):
        """Log file access"""
        query = """
            INSERT INTO access_logs (cid, accessor_bcid, access_type, success)
            VALUES (%s, %s, %s, %s)
        """
        self.cursor.execute(query, (cid, accessor_bcid, access_type, success))
        self.conn.commit()
    
    def _check_policy_match(self, user_attrs, policy):
        """Check if user attributes match file policy"""
        for key, value in policy.items():
            if key not in user_attrs or user_attrs[key] != value:
                return False
        return True
    
    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()
