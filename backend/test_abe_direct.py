# test_abe_direct.py - Test underscores
import sys
sys.path.append('/app')

from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07

print("\n=== Testing Underscores in Attributes ===\n")

group = PairingGroup('SS512')
cpabe = CPabe_BSW07(group)
(pk, mk) = cpabe.setup()

# Test with underscore
print("Test: ROLE_ENGINEER")
try:
    key = cpabe.keygen(pk, mk, ['ROLE_ENGINEER'])
    msg = group.random(GT)
    ct = cpabe.encrypt(pk, msg, 'ROLE_ENGINEER')
    dec = cpabe.decrypt(pk, key, ct)
    print(f"Result: {dec == msg}\n")
except Exception as e:
    print(f"ERROR: {e}\n")

# Test with dash
print("Test: ROLE-ENGINEER")
try:
    key = cpabe.keygen(pk, mk, ['ROLE-ENGINEER'])
    msg = group.random(GT)
    ct = cpabe.encrypt(pk, msg, 'ROLE-ENGINEER')
    dec = cpabe.decrypt(pk, key, ct)
    print(f"Result: {dec == msg}\n")
except Exception as e:
    print(f"ERROR: {e}\n")

# Test with no separator
print("Test: ROLEENGINEER")
try:
    key = cpabe.keygen(pk, mk, ['ROLEENGINEER'])
    msg = group.random(GT)
    ct = cpabe.encrypt(pk, msg, 'ROLEENGINEER')
    dec = cpabe.decrypt(pk, key, ct)
    print(f"Result: {dec == msg}\n")
except Exception as e:
    print(f"ERROR: {e}\n")
