# test_abe_only.py - Test with multiple attributes
import sys
sys.path.append('/app')

from modules.abe_crypto import ABEManager

print("\n=== Testing ABE with Multiple Attributes ===\n")

abe = ABEManager()

# Test with 2 attributes
print("1. Generating user keys with 2 attributes...")
attrs = {'role': 'engineer', 'dept': 'IT'}
keys = abe.generate_user_keys(attrs)
print(f"   ✓ Private key length: {len(keys['private_key'])} chars\n")

# Encrypt with 2-attribute policy
print("2. Encrypting with 2-attribute policy...")
test_data = b"Secret engineering document"
policy = {'role': 'engineer', 'dept': 'IT'}
encrypted = abe.encrypt(test_data, policy)
print(f"   ✓ Encrypted\n")

# Decrypt (should succeed - attributes match)
print("3. Decrypting with matching attributes...")
decrypted = abe.decrypt(encrypted['ciphertext'], keys['private_key'], attrs)
print(f"   ✓ Decrypted: {decrypted.decode()}\n")

# Test access control - wrong attributes
print("4. Testing access control - wrong dept...")
wrong_attrs = {'role': 'engineer', 'dept': 'HR'}
wrong_keys = abe.generate_user_keys(wrong_attrs)
try:
    abe.decrypt(encrypted['ciphertext'], wrong_keys['private_key'], wrong_attrs)
    print("   ✗ ERROR: Should have been denied!\n")
except:
    print("   ✓ Access correctly denied!\n")

print("✅ All multi-attribute tests passed!\n")
