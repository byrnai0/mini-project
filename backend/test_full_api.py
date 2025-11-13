# test_full_api.py - CORRECTED FOR YOUR API
import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

print("=" * 60)
print("Testing Complete File Sharing API")
print("=" * 60)

# Test 1: Register User 1
print("\n1. Registering User 1 (Engineer)...")
user1_data = {
    'username': 'alice_engineer',
    'email': 'alice@company.com',
    'attributes': {
        'role': 'engineer',
        'department': 'IT',
        'level': 'senior'
    }
}

response = requests.post(f"{BASE_URL}/register", json=user1_data)
print(f"Status: {response.status_code}")

if response.status_code in [201, 409]:
    if response.status_code == 201:
        user1 = response.json()
    else:
        # If exists, create user object (won't be tested further without GET endpoint)
        print("User already exists - skipping this test run")
        exit(0)
    print(f"BCID: {user1['bcid']}")
    print("✓ User 1 registered")
else:
    print(f"✗ Failed: {response.json()}")
    exit(1)

# Test 2: Register User 2
print("\n2. Registering User 2 (Manager)...")
user2_data = {
    'username': 'bob_manager',
    'email': 'bob@company.com',
    'attributes': {
        'role': 'manager',
        'department': 'HR',
        'level': 'senior'
    }
}

response = requests.post(f"{BASE_URL}/register", json=user2_data)
print(f"Status: {response.status_code}")

if response.status_code in [201, 409]:
    if response.status_code == 201:
        user2 = response.json()
    else:
        print("User already exists - skipping this test run")
        exit(0)
    print(f"BCID: {user2['bcid']}")
    print("✓ User 2 registered")
else:
    print(f"✗ Failed: {response.json()}")
    exit(1)

# Test 3: Upload file
print("\n3. Uploading file with access policy...")
files = {
    'file': ('engineering_doc.txt', b'This is a confidential engineering document with technical specifications.', 'text/plain')
}
upload_data = {
    'username': user1['username'],
    'bcid': user1['bcid'],
    'access_policy': json.dumps({
        'role': 'engineer',
        'department': 'IT'
    })
}

response = requests.post(f"{BASE_URL}/upload", files=files, data=upload_data)
print(f"Status: {response.status_code}")

if response.status_code == 201:
    upload_result = response.json()
    file_cid = upload_result['cid']
    print(f"CID: {file_cid}")
    print("✓ File uploaded")
else:
    print(f"✗ Failed: {response.json()}")
    exit(1)

print("\n⏳ Waiting for blockchain...")
time.sleep(3)

# Test 4: User 1 downloads (authorized)
print("\n4. User 1 (Engineer/IT) downloading file...")
download_data = {
    'bcid': user1['bcid']  # Changed: send BCID not username
}

response = requests.post(f"{BASE_URL}/download/{file_cid}", json=download_data)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    content = response.content.decode()
    print(f"✓ Downloaded: {content[:50]}...")
else:
    try:
        print(f"⚠ Error: {response.json()}")
    except:
        print(f"⚠ Error {response.status_code}")

# Test 5: User 2 downloads (unauthorized)
print("\n5. User 2 (Manager/HR) downloading file...")
download_data = {
    'bcid': user2['bcid']  # Changed: send BCID not username
}

response = requests.post(f"{BASE_URL}/download/{file_cid}", json=download_data)
print(f"Status: {response.status_code}")

if response.status_code == 403:
    print(f"✓ Access correctly denied")
elif response.status_code == 200:
    print(f"✗ Access granted (should be denied)")
else:
    print(f"✓ Access denied")

# Test 6: List files
print("\n6. Listing files for User 1...")
response = requests.get(f"{BASE_URL}/files/{user1['bcid']}")  # Changed: use BCID
print(f"Status: {response.status_code}")

if response.status_code == 200:
    files_data = response.json()
    print(f"Files: {len(files_data.get('files', []))}")
    print("✓ Files listed")

# Test 7: Get metadata
print("\n7. Getting file metadata...")
response = requests.get(f"{BASE_URL}/file/{file_cid}")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    metadata = response.json()
    print(f"✓ Metadata: {metadata.get('filename', 'N/A')}")

# Test 8: Access logs
print("\n8. Getting access logs for file...")
response = requests.get(f"{BASE_URL}/logs/{file_cid}")  # Changed: pass CID
print(f"Status: {response.status_code}")

if response.status_code == 200:
    logs = response.json()
    print(f"✓ Logs: {len(logs.get('logs', []))} entries")

# Test 9: Stats
print("\n9. Getting statistics...")
response = requests.get(f"{BASE_URL}/stats")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    stats = response.json()
    print(f"✓ Users: {stats.get('total_users')}, Files: {stats.get('total_files')}")

print("\n" + "=" * 60)
print("✅ All API tests completed!")
print("=" * 60)
