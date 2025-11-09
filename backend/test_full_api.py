import requests
import json
import io

BASE_URL = "http://localhost:5000/api"

print("\n" + "="*60)
print("Testing Complete File Sharing API")
print("="*60 + "\n")

# Test 1: Register User 1 (Engineer)
print("1. Registering User 1 (Engineer)...")
user1_data = {
    "username": "alice_engineer",
    "email": "alice@company.com",
    "attributes": {
        "role": "engineer",
        "department": "IT",
        "level": "senior"
    }
}
response = requests.post(f"{BASE_URL}/register", json=user1_data)
print(f"Status: {response.status_code}")
user1 = response.json()
print(f"BCID: {user1.get('bcid')}")
print(f"✓ User 1 registered\n")

# Test 2: Register User 2 (Manager)
print("2. Registering User 2 (Manager)...")
user2_data = {
    "username": "bob_manager",
    "email": "bob@company.com",
    "attributes": {
        "role": "manager",
        "department": "HR",
        "level": "senior"
    }
}
response = requests.post(f"{BASE_URL}/register", json=user2_data)
print(f"Status: {response.status_code}")
user2 = response.json()
print(f"BCID: {user2.get('bcid')}")
print(f"✓ User 2 registered\n")

# Test 3: Upload File (accessible to engineers only)
print("3. Uploading file with access policy...")
test_file_content = b"This is a secret engineering document!"
files = {'file': ('secret_doc.txt', io.BytesIO(test_file_content), 'text/plain')}
data = {
    'bcid': user1['bcid'],
    'access_policy': json.dumps({"role": "engineer", "department": "IT"})
}
response = requests.post(f"{BASE_URL}/upload", files=files, data=data)
print(f"Status: {response.status_code}")
upload_result = response.json()
print(f"CID: {upload_result.get('cid')}")
print(f"✓ File uploaded\n")

cid = upload_result['cid']

# Test 4: User 1 (Engineer) downloads file - Should succeed
print("4. User 1 (Engineer) downloading file...")
response = requests.post(
    f"{BASE_URL}/download/{cid}",
    json={'bcid': user1['bcid']}
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"Downloaded: {response.content.decode()}")
    print(f"✓ Access granted (expected)\n")
else:
    print(f"✗ Access denied (unexpected): {response.json()}\n")

# Test 5: User 2 (Manager) tries to download - Should fail
print("5. User 2 (Manager) downloading file...")
response = requests.post(
    f"{BASE_URL}/download/{cid}",
    json={'bcid': user2['bcid']}
)
print(f"Status: {response.status_code}")
if response.status_code == 403:
    print(f"Access denied: {response.json().get('error')}")
    print(f"✓ Access control working (expected)\n")
else:
    print(f"✗ Access granted (unexpected)\n")

# Test 6: List files for User 1
print("6. Listing files for User 1...")
response = requests.get(f"{BASE_URL}/files/{user1['bcid']}")
print(f"Status: {response.status_code}")
files_list = response.json()
print(f"Owned files: {files_list['total_owned']}")
print(f"Accessible files: {files_list['total_accessible']}")
print(f"✓ File listing retrieved\n")

# Test 7: Get file metadata
print("7. Getting file metadata...")
response = requests.get(f"{BASE_URL}/file/{cid}")
print(f"Status: {response.status_code}")
metadata = response.json()
print(f"Filename: {metadata.get('filename')}")
print(f"Owner: {metadata.get('owner')}")
print(f"Policy: {metadata.get('access_policy')}")
print(f"✓ Metadata retrieved\n")

# Test 8: Get access logs
print("8. Getting access logs...")
response = requests.get(f"{BASE_URL}/logs/{cid}")
print(f"Status: {response.status_code}")
logs = response.json()
print(f"Total accesses: {logs.get('total_accesses')}")
for log in logs.get('logs', []):
    print(f"  - {log['accessor']} ({log['access_type']}): {'✓' if log['success'] else '✗'}")
print(f"✓ Access logs retrieved\n")

# Test 9: Get system statistics
print("9. Getting system statistics...")
response = requests.get(f"{BASE_URL}/stats")
print(f"Status: {response.status_code}")
stats = response.json()
print(f"Total users: {stats.get('users')}")
print(f"Total files: {stats.get('files')}")
print(f"Total accesses: {stats.get('total_accesses')}")
print(f"✓ Statistics retrieved\n")

print("="*60)
print("✅ All API tests completed!")
print("="*60 + "\n")
