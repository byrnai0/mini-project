# modules/abe_crypto.py - SIMPLIFIED VERSION WITHOUT CHARM

import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import json

class ABEManager:
    """Simplified ABE Manager using symmetric encryption"""
    
    def __init__(self):
        print("✅ ABE Encryption Manager initialized")
        self.backend = default_backend()
        self.master_key = Fernet.generate_key()
        self.master_cipher = Fernet(self.master_key)
        print("✓ Master keys generated")
    
    def _attributes_to_tags(self, attributes):
        """Convert attribute dict to unique tags"""
        tags = [f"{k.upper()}-{v.upper()}" for k, v in attributes.items()]
        return tags
    
    def generate_user_keys(self, attributes):
        """Generate encryption keys for user based on their attributes"""
        attr_tags = self._attributes_to_tags(attributes)
        
        print(f"Generating keys for attributes: {attr_tags}")
        
        # Create deterministic key from attributes
        attr_string = "|".join(sorted(attr_tags))
        
        # Derive key using hashlib.pbkdf2_hmac (built-in, no cryptography needed)
        key_material = hashlib.pbkdf2_hmac(
            'sha256',
            attr_string.encode(),
            b'secure_file_share',
            100000
        )
        private_key = base64.b64encode(key_material).decode('utf-8')
        
        # Master public key
        public_key = base64.b64encode(self.master_key).decode('utf-8')
        
        print(f"✓ Keys generated successfully")
        
        return {
            'private_key': private_key,
            'public_key': public_key,
            'attributes': attributes
        }
    
    def encrypt(self, data: bytes, policy: dict) -> bytes:
        try:
            if not isinstance(data, (bytes, bytearray)):
                data = str(data).encode()

            key = os.urandom(32)   # AES-256 key
            iv = os.urandom(12)    # GCM IV
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=self.backend)
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(data) + encryptor.finalize()
            tag = encryptor.tag

            metadata = {
                "key": key.hex(),
                "iv": iv.hex(),
                "tag": tag.hex(),
                "policy": policy
            }

            result = json.dumps(metadata).encode() + b"|||" + ciphertext

            print(f"✅ ABE.encrypt: encrypted {len(data)} bytes -> ciphertext {len(ciphertext)} bytes")
            print(f"   policy: {policy}")

            return result
        except Exception as e:
            print(f"❌ ABE.encrypt error: {e}")
            raise

    def decrypt(self, encrypted_blob: bytes, user_attributes: dict) -> bytes:
        """
        Decrypt encrypted_blob produced by encrypt().
        The second parameter user_attributes is required and used to verify policy.
        """
        try:
            if not isinstance(encrypted_blob, (bytes, bytearray)):
                raise ValueError("encrypted_blob must be bytes")

            parts = encrypted_blob.split(b"|||", 1)
            if len(parts) != 2:
                raise ValueError("Invalid encrypted format")

            metadata = json.loads(parts[0].decode())
            ciphertext = parts[1]

            policy = metadata.get("policy", {})
            # Check if policy allows current user
            for k, v in policy.items():
                user_val = user_attributes.get(k)
                if user_val is None:
                    raise PermissionError(f"Access policy not satisfied: missing required attribute '{k}'")
                
                # Support both single value and list of allowed values
                allowed_values = v if isinstance(v, list) else [v]
                if str(user_val).lower() not in [str(av).lower() for av in allowed_values]:
                    raise PermissionError(f"Access policy not satisfied: required {k} in {allowed_values}, but got {k}={user_val}")

            key = bytes.fromhex(metadata["key"])
            iv = bytes.fromhex(metadata["iv"])
            tag = bytes.fromhex(metadata["tag"])

            cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=self.backend)
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            print(f"✅ ABE.decrypt: decrypted ciphertext {len(ciphertext)} bytes -> {len(plaintext)} bytes")
            print(f"   user_attributes: {user_attributes}")
            print(f"   policy: {policy}")

            return plaintext
        except Exception as e:
            print(f"❌ ABE.decrypt error: {e}")
            raise
    
    def check_access(self, user_attributes, access_policy):
        """Check if user attributes satisfy access policy"""
        if not access_policy:
            return True
            
        for key, value in access_policy.items():
            if key not in user_attributes or user_attributes[key] != value:
                print(f"Access denied: missing or mismatched attribute {key}")
                return False
        
        print(f"Access granted: attributes match policy")
        return True

# Example usage
if __name__ == "__main__":
    abe_manager = ABEManager()

    file_data = b"Hello, World!"
    policy = {"role": ["manager", "hr"]}  # NOW allows both roles
    encrypted_data = abe_manager.encrypt(file_data, policy)

    print(f"Encrypted data: {encrypted_data}")

    user_attributes = {"role": "manager"}
    decrypted_data = abe_manager.decrypt(encrypted_data, user_attributes)

    print(f"Decrypted data: {decrypted_data}")
