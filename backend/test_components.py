import sys
sys.path.append('/app')

from modules.blockchain import BlockchainManager
from modules.ipfs_storage import IPFSManager
import json

print("\n=== Testing Backend Components ===\n")

# Test 1: Blockchain
print("1. Testing Blockchain connection...")
try:
    blockchain = BlockchainManager()
    print("   ✓ Blockchain connected")
    print(f"   ✓ Contract loaded")
except Exception as e:
    print(f"   ✗ Blockchain failed: {e}")

# Test 2: IPFS
print("\n2. Testing IPFS connection...")
try:
    ipfs = IPFSManager()
    
    # Upload test data
    test_data = b"Test file content"
    cid = ipfs.upload(test_data)
    print(f"   ✓ File uploaded to IPFS")
    print(f"   CID: {cid}")
    
    # Download test data
    retrieved = ipfs.download(cid)
    assert retrieved == test_data
    print(f"   ✓ File retrieved from IPFS")
    
except Exception as e:
    print(f"   ✗ IPFS failed: {e}")

print("\n✅ Component tests complete!\n")
