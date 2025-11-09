from charm.toolbox.pairinggroup import PairingGroup
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
import json

def test_charm():
    print("\n=== Testing Charm-crypto ===\n")
    
    # 1. Initialize pairing group
    print("1. Initializing pairing group...")
    group = PairingGroup('SS512')
    print("   ✓ Pairing group created")
    
    # 2. Initialize CP-ABE scheme
    print("\n2. Initializing CP-ABE scheme...")
    cpabe = CPabe_BSW07(group)
    print("   ✓ CP-ABE scheme loaded")
    
    # 3. Setup - Generate master keys
    print("\n3. Generating master keys...")
    (master_public_key, master_key) = cpabe.setup()
    print("   ✓ Master public key generated")
    print("   ✓ Master secret key generated")
    
    # 4. Key Generation - User with attributes
    print("\n4. Generating user keys...")
    user_attributes = ['role:engineer', 'dept:IT', 'level:senior']
    print(f"   User attributes: {user_attributes}")
    
    user_key = cpabe.keygen(master_public_key, master_key, user_attributes)
    print("   ✓ User private key generated")
    
    # 5. Encryption - Encrypt data with policy
    print("\n5. Encrypting data...")
    policy = '(role:engineer and dept:IT)'
    message = b"This is a secret file for IT engineers only!"
    print(f"   Policy: {policy}")
    print(f"   Message: {message.decode()}")
    
    ciphertext = cpabe.encrypt(master_public_key, message, policy)
    print("   ✓ Data encrypted successfully")
    
    # 6. Decryption - Decrypt with matching attributes
    print("\n6. Decrypting data...")
    try:
        plaintext = cpabe.decrypt(master_public_key, user_key, ciphertext)
        print(f"   ✓ Decryption successful!")
        print(f"   Decrypted message: {plaintext.decode()}")
        
        # Verify
        assert plaintext == message
        print("   ✓ Message integrity verified")
    except Exception as e:
        print(f"   ✗ Decryption failed: {e}")
        return False
    
    # 7. Test access denial
    print("\n7. Testing access control...")
    wrong_attributes = ['role:manager', 'dept:HR']
    wrong_user_key = cpabe.keygen(master_public_key, master_key, wrong_attributes)
    
    try:
        cpabe.decrypt(master_public_key, wrong_user_key, ciphertext)
        print("   ✗ Access control failed - unauthorized user could decrypt!")
        return False
    except:
        print("   ✓ Access denied for unauthorized user (expected)")
    
    print("\n✅ All Charm-crypto tests passed!\n")
    return True

if __name__ == '__main__':
    success = test_charm()
    exit(0 if success else 1)
