# test_abe_only.py
import sys
sys.path.append('/app')

from modules.abe_crypto import ABEManager

print("\n=== Testing ABE Serialization ===\n")

# Initialize ABE
abe = ABEManager()

# Test 1: Generate keys
print("1. Generating user keys...")
attrs = {'role': 'engineer', 'dept': 'IT'}
keys = abe.generate_user_keys(attrs)
print(f"   ✓ Private key: {keys['private_key'][:50]}...")
print(f"   ✓ Key length: {len(keys['private_key'])} chars\n")

# Test 2: Encrypt
print("2. Encrypting data...")
test_data = b"Secret message"
policy = {'role': 'engineer', 'dept': 'IT'}
encrypted = abe.encrypt(test_data, policy)
print(f"   ✓ Encrypted: {encrypted['ciphertext'][:50]}...\n")

# Test 3: Decrypt
print("3. Decrypting data...")
decrypted = abe.decrypt(
    encrypted['ciphertext'],
    keys['private_key'],
    attrs
)
print(f"   ✓ Decrypted: {decrypted.decode()}\n")

# Test 4: Verify
assert decrypted == test_data
print("✅ All ABE tests passed!\n")
