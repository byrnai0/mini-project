import os
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64

class ABEService:
    """
    Simplified CP-ABE implementation using hybrid encryption
    
    Real ABE is complex (requires Charm-Crypto library)
    For prototype: We'll simulate ABE logic with policy-based key derivation
    """
    
    def __init__(self):
        # Master secret key (in production, this should be in HSM)
        self.master_key = os.getenv('ABE_MASTER_KEY', 'master-secret-key-do-not-share')
    
    def generate_policy_key(self, policy: dict) -> bytes:
        """
        Generate encryption key based on access policy
        policy = {'role': 'manager', 'department': 'IT', 'clearance': 3}
        """
        # Sort policy for consistency
        policy_str = json.dumps(policy, sort_keys=True)
        
        # Derive key using PBKDF2
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'abe_salt_v1',  # In production, use random salt per file
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(policy_str.encode()))
        return key
    
    def encrypt_file(self, file_data: bytes, access_policy: dict) -> dict:
        """
        Encrypt file with ABE policy
        Returns: {
            'encrypted_data': bytes,
            'policy': dict,
            'metadata': dict
        }
        """
        try:
            # Generate symmetric key for file encryption (faster for large files)
            file_key = Fernet.generate_key()
            fernet = Fernet(file_key)
            
            # Encrypt file data
            encrypted_file = fernet.encrypt(file_data)
            
            # Encrypt the file key with policy-based key (this is the ABE part)
            policy_key = self.generate_policy_key(access_policy)
            key_fernet = Fernet(policy_key)
            encrypted_file_key = key_fernet.encrypt(file_key)
            
            return {
                'encrypted_data': encrypted_file,
                'encrypted_key': base64.b64encode(encrypted_file_key).decode(),
                'policy': access_policy,
                'encryption_version': 'v1'
            }
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def decrypt_file(self, encrypted_data: bytes, encrypted_key: str, 
                     user_attributes: dict, file_policy: dict) -> bytes:
        """
        Decrypt file if user attributes match policy
        """
        try:
            # Check if user attributes satisfy policy
            if not self._evaluate_policy(user_attributes, file_policy):
                raise PermissionError("User attributes do not match file access policy")
            
            # Regenerate policy key
            policy_key = self.generate_policy_key(file_policy)
            key_fernet = Fernet(policy_key)
            
            # Decrypt file key
            file_key = key_fernet.decrypt(base64.b64decode(encrypted_key))
            
            # Decrypt file
            fernet = Fernet(file_key)
            decrypted_data = fernet.decrypt(encrypted_data)
            
            return decrypted_data
        except PermissionError:
            raise
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")
    
    def _evaluate_policy(self, user_attributes: dict, policy: dict) -> bool:
        """
        Check if user attributes satisfy the access policy
        
        Simple implementation: All policy attributes must match user attributes
        Advanced: Implement AND/OR logic, threshold policies
        """
        for key, value in policy.items():
            if key not in user_attributes:
                return False
            if user_attributes[key] != value:
                return False
        return True
    
    def create_access_policy(self, **kwargs) -> dict:
        """
        Helper to create access policies
        Example: create_access_policy(role='manager', department='IT')
        """
        return {k: v for k, v in kwargs.items() if v is not None}