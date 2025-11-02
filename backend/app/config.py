import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Config
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-this')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    
    # MongoDB Config
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = 'secure_file_sharing'
    
    # IPFS Config
    IPFS_HOST = os.getenv('IPFS_HOST', '/ip4/127.0.0.1/tcp/5001')
    
    # Blockchain Config (prepare interface for blockchain team)
    BLOCKCHAIN_RPC_URL = os.getenv('BLOCKCHAIN_RPC_URL', 'http://127.0.0.1:8545')
    CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS', '')
    
    # File Upload Config
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx', 'xlsx', 'jpg', 'png'}
    
    # ABE Config
    ABE_CURVE = 'SS512'  # Elliptic curve for ABE