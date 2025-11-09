# modules/abe_crypto.py - HYBRID ENCRYPTION (CORRECT APPROACH)
from charm.toolbox.pairinggroup import ZR  # Add this to imports
from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from charm.core.engine.util import objectToBytes, bytesToObject
from charm.toolbox.symcrypto import SymmetricCryptoAbstraction
import json
import base64

class ABEManager:
    def __init__(self):
        # Initialize pairing group
        self.group = PairingGroup('SS512')
        
        # Initialize CP-ABE scheme
        self.cpabe = CPabe_BSW07(self.group)
        
        # Generate master keys
        self.master_public_key, self.master_key = self.cpabe.setup()
        
        print("✓ ABE Manager initialized")
        print("✓ Master keys generated")
    
    def generate_user_keys(self, attributes):
        """
        Generate ABE keys for user based on their attributes
        Args:
            attributes: dict - e.g., {'role': 'engineer', 'department': 'IT'}
        Returns:
            dict - Contains private_key, public_key, attributes
        """
        # Convert attributes dict to list format for Charm
        attr_list = [f"{k}:{v}" for k, v in attributes.items()]
        
        print(f"Generating keys for attributes: {attr_list}")
        
        # Generate private key for these attributes
        private_key = self.cpabe.keygen(
            self.master_public_key,
            self.master_key,
            attr_list
        )
        
        # Serialize private key
        try:
            private_key_bytes = objectToBytes(private_key, self.group)
            private_key_serialized = base64.b64encode(private_key_bytes).decode('utf-8')
            
            public_key_bytes = objectToBytes(self.master_public_key, self.group)
            public_key_serialized = base64.b64encode(public_key_bytes).decode('utf-8')
            
            print(f"✓ Keys serialized successfully")
            
            return {
                'private_key': private_key_serialized,
                'public_key': public_key_serialized,
                'attributes': attributes
            }
        except Exception as e:
            raise Exception(f"Key serialization failed: {str(e)}")
    
    def encrypt(self, data, access_policy):
        """
        Encrypt data with ABE using access policy
        Uses hybrid encryption: ABE encrypts a symmetric key, symmetric crypto encrypts data
        
        Args:
            data: bytes - Data to encrypt
            access_policy: dict - e.g., {'role': 'engineer', 'department': 'IT'}
        Returns:
            dict - Contains ciphertext and metadata
        """
        # Create policy string from dict
        policy_parts = [f"{k}:{v}" for k, v in access_policy.items()]
        policy_str = "(" + " and ".join(policy_parts) + ")"
        
        print(f"Encrypting with policy: {policy_str}")
        
        try:
            # Step 1: Generate random symmetric key (GT element)
            symmetric_key = self.group.random(GT)
            
            # Step 2: Encrypt the symmetric key with CP-ABE
            abe_ciphertext = self.cpabe.encrypt(
                self.master_public_key,
                symmetric_key,
                policy_str
            )
            
            # Step 3: Serialize ABE ciphertext
            abe_ct_bytes = objectToBytes(abe_ciphertext, self.group)
            abe_ct_b64 = base64.b64encode(abe_ct_bytes).decode('utf-8')
            
            # Step 4: Derive AES key from symmetric_key
            aes_key = self.group.hash(symmetric_key, ZR=True)
            symmetric_cipher = SymmetricCryptoAbstraction(aes_key)
            
            # Step 5: Encrypt actual data with AES
            data_ciphertext = symmetric_cipher.encrypt(data)
            data_ct_b64 = base64.b64encode(data_ciphertext).decode('utf-8')
            
            # Combine both ciphertexts
            combined = {
                'abe_ciphertext': abe_ct_b64,      # ABE-encrypted symmetric key
                'data_ciphertext': data_ct_b64,     # AES-encrypted data
                'policy': policy_str
            }
            
            combined_json = json.dumps(combined)
            
            print(f"✓ Data encrypted successfully (hybrid encryption)")
            
            return {
                'ciphertext': combined_json.encode('utf-8'),
                'policy': policy_str,
                'policy_dict': access_policy
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception(f"Encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_data, user_private_key, user_attributes):
        """
        Decrypt data using user's private key
        
        Args:
            encrypted_data: bytes - Serialized ciphertext
            user_private_key: str - Base64-encoded private key
            user_attributes: dict - User's attributes
        Returns:
            bytes - Decrypted plaintext
        """
        try:
            # Parse combined ciphertext
            if isinstance(encrypted_data, bytes):
                encrypted_str = encrypted_data.decode('utf-8')
            else:
                encrypted_str = encrypted_data
            
            combined = json.loads(encrypted_str)
            
            # Deserialize ABE ciphertext
            abe_ct_bytes = base64.b64decode(combined['abe_ciphertext'])
            abe_ciphertext = bytesToObject(abe_ct_bytes, self.group)
            
            # Deserialize private key
            private_key_bytes = base64.b64decode(user_private_key)
            private_key = bytesToObject(private_key_bytes, self.group)
            
            print(f"Attempting decryption with attributes: {user_attributes}")
            
            # Step 1: Decrypt symmetric key using ABE
            symmetric_key = self.cpabe.decrypt(
                self.master_public_key,
                private_key,
                abe_ciphertext
            )
            
            if not symmetric_key:
                raise Exception("ABE decryption failed - attributes don't satisfy policy")
            
            # Step 2: Derive AES key from symmetric_key
            from charm.toolbox.pairinggroup import ZR
            aes_key = self.group.hash(symmetric_key, ZR=True)
            symmetric_cipher = SymmetricCryptoAbstraction(aes_key)
            
            # Step 3: Decrypt data with AES
            data_ct_bytes = base64.b64decode(combined['data_ciphertext'])
            plaintext = symmetric_cipher.decrypt(data_ct_bytes)
            
            print("✓ Decryption successful")
            return plaintext
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception(f"Decryption failed: {str(e)}")
    
    def check_access(self, user_attributes, access_policy):
        """
        Check if user attributes satisfy access policy
        """
        for key, value in access_policy.items():
            if key not in user_attributes or user_attributes[key] != value:
                return False
        return True
