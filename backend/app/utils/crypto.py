import hashlib
import secrets

def generate_salt(length: int = 32) -> str:
    """Generate random salt for cryptographic operations"""
    return secrets.token_hex(length)

def hash_data(data: str, salt: str = "") -> str:
    """Hash data using SHA-256"""
    return hashlib.sha256(f"{data}{salt}".encode()).hexdigest()

def generate_api_key() -> str:
    """Generate secure API key"""
    return secrets.token_urlsafe(32)