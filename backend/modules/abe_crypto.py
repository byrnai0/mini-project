# modules/abe_crypto.py - FINAL WORKING VERSION

from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from charm.core.engine.util import objectToBytes, bytesToObject
from charm.toolbox.symcrypto import SymmetricCryptoAbstraction
from hashlib import sha256
import json
import base64

class ABEManager:
    def __init__(self):
        self.group = PairingGroup('SS512')
        self.cpabe = CPabe_BSW07(self.group)
        self.master_public_key, self.master_key = self.cpabe.setup()
        print("✓ ABE Manager initialized")
        print("✓ Master keys generated")
    
    def _attributes_to_tags(self, attributes):
        """
        Convert attribute dict to unique tags using dashes
        Example: {'role': 'engineer', 'dept': 'IT'} -> ['ROLE-ENGINEER', 'DEPT-IT']
        """
        tags = [f"{k.upper()}-{v.upper()}" for k, v in attributes.items()]
        return tags
    
    def generate_user_keys(self, attributes):
        """Generate ABE keys for user based on their attributes"""
        # Convert to unique tags
        attr_tags = self._attributes_to_tags(attributes)
        
        print(f"Generating keys for attributes: {attr_tags}")
        
        private_key = self.cpabe.keygen(
            self.master_public_key,
            self.master_key,
            attr_tags
        )
        
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
    
    def encrypt(self, data, access_policy):
        """Encrypt data using hybrid encryption (ABE + AES)"""
        # Convert policy to unique tags
        policy_tags = self._attributes_to_tags(access_policy)
        
        # Create policy string
        if len(policy_tags) == 1:
            policy_str = policy_tags[0]
        else:
            policy_str = " and ".join(policy_tags)
        
        print(f"Encrypting with policy: {policy_str}")
        
        # Generate random symmetric key
        symmetric_key = self.group.random(GT)
        
        # Encrypt symmetric key with CP-ABE
        abe_ciphertext = self.cpabe.encrypt(
            self.master_public_key,
            symmetric_key,
            policy_str
        )
        
        if abe_ciphertext is None:
            raise Exception(f"ABE encryption failed - invalid policy: {policy_str}")
        
        # Serialize ABE ciphertext
        abe_ct_bytes = objectToBytes(abe_ciphertext, self.group)
        abe_ct_b64 = base64.b64encode(abe_ct_bytes).decode('utf-8')
        
        # Derive AES key
        symmetric_key_bytes = objectToBytes(symmetric_key, self.group)
        aes_key_bytes = sha256(symmetric_key_bytes).digest()
        
        # Encrypt data with AES
        symmetric_cipher = SymmetricCryptoAbstraction(aes_key_bytes)
        data_ciphertext = symmetric_cipher.encrypt(data)
        
        if isinstance(data_ciphertext, bytes):
            data_ct_b64 = base64.b64encode(data_ciphertext).decode('utf-8')
        else:
            data_ct_b64 = data_ciphertext
        
        # Combine ciphertexts
        combined = {
            'abe_ciphertext': abe_ct_b64,
            'data_ciphertext': data_ct_b64,
            'policy': policy_str
        }
        
        combined_json = json.dumps(combined)
        
        print(f"✓ Data encrypted successfully (hybrid encryption)")
        
        return {
            'ciphertext': combined_json.encode('utf-8'),
            'policy': policy_str,
            'policy_dict': access_policy
        }
    
    def decrypt(self, encrypted_data, user_private_key, user_attributes):
        """Decrypt data using user's private key"""
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
        
        # Decrypt symmetric key using ABE
        symmetric_key = self.cpabe.decrypt(
            self.master_public_key,
            private_key,
            abe_ciphertext
        )
        
        if symmetric_key is False or symmetric_key is None:
            raise Exception("Attributes don't satisfy policy")
        
        # Derive AES key
        symmetric_key_bytes = objectToBytes(symmetric_key, self.group)
        aes_key_bytes = sha256(symmetric_key_bytes).digest()
        
        # Decrypt data with AES
        symmetric_cipher = SymmetricCryptoAbstraction(aes_key_bytes)
        data_ct_str = combined['data_ciphertext']
        plaintext = symmetric_cipher.decrypt(data_ct_str)
        
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        print("✓ Decryption successful")
        return plaintext
    
    def check_access(self, user_attributes, access_policy):
        """Check if user attributes satisfy access policy"""
        for key, value in access_policy.items():
            if key not in user_attributes or user_attributes[key] != value:
                return False
        return True
