import os

class Config:
    # Flask settings
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Database settings
    DATABASE_HOST = os.getenv('DATABASE_HOST', 'mysql')
    DATABASE_USER = os.getenv('DATABASE_USER', 'root')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'password123')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'file_sharing_db')
    
    # Blockchain settings
    GANACHE_URL = os.getenv('GANACHE_URL', 'http://ganache:8545')
    CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS', '')
    
    # IPFS settings
    IPFS_HOST = os.getenv('IPFS_HOST', 'ipfs')
    IPFS_PORT = int(os.getenv('IPFS_PORT', '5001'))
