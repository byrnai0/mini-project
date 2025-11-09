# app.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from modules.blockchain import BlockchainManager
from modules.abe_crypto import ABEManager
from modules.ipfs_storage import IPFSManager
from modules.database import DatabaseManager
import uuid
import json
import io
import os

app = Flask(__name__)
CORS(app)

# Initialize managers
print("\n=== Initializing Backend Services ===\n")
try:
    blockchain = BlockchainManager()
    abe = ABEManager()
    ipfs = IPFSManager()
    db = DatabaseManager()
    print("\n✅ All services initialized successfully!\n")
except Exception as e:
    print(f"\n✗ Failed to initialize services: {e}\n")
    exit(1)

# ============== Health Check ==============
@app.route('/')
def home():
    return jsonify({
        'status': 'running',
        'message': 'Secure File Sharing Backend with ABE & Blockchain',
        'version': '1.0.0',
        'services': {
            'blockchain': 'connected',
            'ipfs': 'connected',
            'database': 'connected',
            'abe': 'initialized'
        }
    })

@app.route('/health')
def health():
    """Comprehensive health check"""
    try:
        # Check all services
        health_status = {
            'backend': 'healthy',
            'blockchain': 'connected' if blockchain.w3.is_connected() else 'disconnected',
            'ipfs': 'connected',
            'database': 'connected',
            'abe': 'initialized'
        }
        return jsonify(health_status), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== User Management ==============
# app.py - Fix the register endpoint

@app.route('/api/register', methods=['POST'])
def register_user():
    """
    Register a new user
    Body: {
        "username": "john_doe",
        "email": "john@example.com",
        "attributes": {
            "role": "engineer",
            "department": "IT",
            "level": "senior"
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data.get('username') or not data.get('email') or not data.get('attributes'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        username = data['username']
        email = data['email']
        attributes = data['attributes']
        
        # Check if user already exists
        existing_user = db.get_user_by_email(email)
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Generate unique Blockchain ID
        bcid = f"BCID_{uuid.uuid4().hex[:16].upper()}"
        
        # Generate ABE keys for user
        print(f"\nGenerating keys for user: {username}")
        user_keys = abe.generate_user_keys(attributes)
        
        # Get user count to assign Ethereum address (FIX THIS PART)
        db.cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = db.cursor.fetchone()['count']
        user_eth_address = blockchain.w3.eth.accounts[user_count % 10]
        
        # Register user on blockchain
        print(f"Registering user on blockchain...")
        tx_hash = blockchain.register_user(bcid, user_keys['public_key'], user_eth_address)
        
        # Store user in database
        db.insert_user({
            'bcid': bcid,
            'username': username,
            'email': email,
            'attributes': json.dumps(attributes),
            'private_key': user_keys['private_key'],
            'ethereum_address': user_eth_address,
            'tx_hash': tx_hash
        })
        
        print(f"✓ User registered: {username} ({bcid})")
        
        return jsonify({
            'success': True,
            'bcid': bcid,
            'username': username,
            'email': email,
            'attributes': attributes,
            'ethereum_address': user_eth_address,
            'tx_hash': tx_hash,
            'message': 'User registered successfully'
        }), 201
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full error trace
        return jsonify({'error': str(e)}), 400

@app.route('/api/user/<bcid>', methods=['GET'])
def get_user(bcid):
    """Get user information by BCID"""
    try:
        user = db.get_user_by_bcid(bcid)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Don't return private key
        user_info = {
            'bcid': user['bcid'],
            'username': user['username'],
            'email': user['email'],
            'attributes': json.loads(user['attributes']),
            'ethereum_address': user['ethereum_address'],
            'created_at': str(user['created_at'])
        }
        
        return jsonify(user_info), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============== File Upload ==============
@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Upload and encrypt a file
    Form Data:
        file: File to upload
        bcid: User's blockchain ID
        access_policy: JSON string of required attributes
    """
    try:
        # Validate inputs
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        bcid = request.form.get('bcid')
        access_policy = json.loads(request.form.get('access_policy', '{}'))
        
        if not bcid:
            return jsonify({'error': 'BCID is required'}), 400
        
        if not access_policy:
            return jsonify({'error': 'Access policy is required'}), 400
        
        # Verify user exists
        user = db.get_user_by_bcid(bcid)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Read file content
        file_content = file.read()
        file_size = len(file_content)
        
        print(f"\nUploading file: {file.filename} ({file_size} bytes)")
        print(f"Access policy: {access_policy}")
        
        # Encrypt file using ABE
        print("Encrypting file with ABE...")
        encrypted_data = abe.encrypt(file_content, access_policy)
        
        # Upload encrypted file to IPFS
        print("Uploading to IPFS...")
        cid = ipfs.upload(encrypted_data['ciphertext'])
        
        # Pin the file for persistence
        ipfs.pin(cid)
        
        # Store metadata on blockchain
        print("Storing metadata on blockchain...")
        tx_hash = blockchain.share_file(
            cid,
            encrypted_data['policy'],  # Store policy as encrypted key reference
            json.dumps(access_policy),
            user['ethereum_address']
        )
        
        # Store file record in database
        db.insert_file({
            'cid': cid,
            'owner_bcid': bcid,
            'filename': file.filename,
            'file_size': file_size,
            'access_policy': json.dumps(access_policy),
            'tx_hash': tx_hash
        })
        
        # Log upload
        db.log_access(cid, bcid, 'upload', True)
        
        print(f"✓ File uploaded successfully: {cid}")
        
        return jsonify({
            'success': True,
            'cid': cid,
            'filename': file.filename,
            'size': file_size,
            'access_policy': access_policy,
            'tx_hash': tx_hash,
            'message': 'File uploaded and encrypted successfully'
        }), 201
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 400

# ============== File Download ==============
@app.route('/api/download/<cid>', methods=['POST'])
def download_file(cid):
    """
    Download and decrypt a file
    Body: {
        "bcid": "User's blockchain ID"
    }
    """
    try:
        data = request.get_json()
        bcid = data.get('bcid')
        
        if not bcid:
            return jsonify({'error': 'BCID is required'}), 400
        
        # Get user info
        user = db.get_user_by_bcid(bcid)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get file metadata from database
        file_record = db.get_file_by_cid(cid)
        if not file_record:
            return jsonify({'error': 'File not found'}), 404
        
        # Get file metadata from blockchain (for verification)
        blockchain_metadata = blockchain.get_file_metadata(cid)
        
        # Check access policy
        user_attributes = json.loads(user['attributes'])
        access_policy = json.loads(file_record['access_policy'])
        
        print(f"\nDownload request from {user['username']}")
        print(f"User attributes: {user_attributes}")
        print(f"Required policy: {access_policy}")
        
        if not abe.check_access(user_attributes, access_policy):
            db.log_access(cid, bcid, 'download', False)
            return jsonify({
                'error': 'Access denied: Your attributes do not satisfy the file policy',
                'required': access_policy,
                'your_attributes': user_attributes
            }), 403
        
        # Download encrypted file from IPFS
        print("Downloading from IPFS...")
        encrypted_data = ipfs.download(cid)
        
        # Decrypt file
        print("Decrypting file...")
        try:
            decrypted_data = abe.decrypt(
                encrypted_data,
                user['private_key'],
                user_attributes
            )
        except Exception as e:
            db.log_access(cid, bcid, 'download', False)
            return jsonify({'error': f'Decryption failed: {str(e)}'}), 403
        
        # Log successful access
        db.log_access(cid, bcid, 'download', True)
        blockchain.contract.functions.logFileAccess(cid).transact({
            'from': user['ethereum_address']
        })
        
        print(f"✓ File downloaded successfully by {user['username']}")
        
        # Return file as download
        return send_file(
            io.BytesIO(decrypted_data),
            as_attachment=True,
            download_name=file_record['filename'],
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        print(f"Download error: {str(e)}")
        return jsonify({'error': str(e)}), 400

# ============== File Listing ==============
@app.route('/api/files/<bcid>', methods=['GET'])
def list_user_files(bcid):
    """List all files owned by or accessible to a user"""
    try:
        user = db.get_user_by_bcid(bcid)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get files owned by user
        owned_files = db.get_files_by_owner(bcid)
        
        # Get files accessible to user
        user_attributes = json.loads(user['attributes'])
        accessible_files = db.get_accessible_files(user_attributes)
        
        # Format response
        owned = [{
            'cid': f['cid'],
            'filename': f['filename'],
            'size': f['file_size'],
            'access_policy': json.loads(f['access_policy']),
            'uploaded_at': str(f['created_at'])
        } for f in owned_files]
        
        accessible = [{
            'cid': f['cid'],
            'filename': f['filename'],
            'size': f['file_size'],
            'owner': f['owner_bcid'],
            'access_policy': json.loads(f['access_policy']),
            'uploaded_at': str(f['created_at'])
        } for f in accessible_files if f['owner_bcid'] != bcid]
        
        return jsonify({
            'owned_files': owned,
            'accessible_files': accessible,
            'total_owned': len(owned),
            'total_accessible': len(accessible)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============== File Metadata ==============
@app.route('/api/file/<cid>', methods=['GET'])
def get_file_metadata(cid):
    """Get file metadata"""
    try:
        # Get from database
        file_record = db.get_file_by_cid(cid)
        if not file_record:
            return jsonify({'error': 'File not found'}), 404
        
        # Get from blockchain
        blockchain_metadata = blockchain.get_file_metadata(cid)
        
        # Get IPFS info
        ipfs_info = ipfs.get_file_info(cid)
        
        metadata = {
            'cid': cid,
            'filename': file_record['filename'],
            'size': file_record['file_size'],
            'owner': file_record['owner_bcid'],
            'access_policy': json.loads(file_record['access_policy']),
            'uploaded_at': str(file_record['created_at']),
            'blockchain': {
                'owner': blockchain_metadata['owner'],
                'timestamp': blockchain_metadata['timestamp'],
                'tx_hash': file_record['tx_hash']
            },
            'ipfs': ipfs_info
        }
        
        return jsonify(metadata), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============== Access Logs ==============
@app.route('/api/logs/<cid>', methods=['GET'])
def get_access_logs(cid):
    """Get access logs for a file"""
    try:
        query = """
            SELECT al.*, u.username, u.email
            FROM access_logs al
            JOIN users u ON al.accessor_bcid = u.bcid
            WHERE al.cid = %s
            ORDER BY al.accessed_at DESC
        """
        db.cursor.execute(query, (cid,))
        logs = db.cursor.fetchall()
        
        formatted_logs = [{
            'accessor': log['username'],
            'email': log['email'],
            'bcid': log['accessor_bcid'],
            'access_type': log['access_type'],
            'success': bool(log['success']),
            'timestamp': str(log['accessed_at'])
        } for log in logs]
        
        return jsonify({
            'cid': cid,
            'total_accesses': len(formatted_logs),
            'logs': formatted_logs
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============== Statistics ==============
@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Get system statistics"""
    try:
        # User count
        db.cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = db.cursor.fetchone()['count']
        
        # File count
        db.cursor.execute("SELECT COUNT(*) as count FROM files")
        file_count = db.cursor.fetchone()['count']
        
        # Total file size
        db.cursor.execute("SELECT SUM(file_size) as total FROM files")
        total_size = db.cursor.fetchone()['total'] or 0
        
        # Access logs count
        db.cursor.execute("SELECT COUNT(*) as count FROM access_logs")
        access_count = db.cursor.fetchone()['count']
        
        return jsonify({
            'users': user_count,
            'files': file_count,
            'total_storage': total_size,
            'total_accesses': access_count,
            'blockchain': {
                'network': 'Ganache Local',
                'contract_address': blockchain.contract.address
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Starting File Sharing Backend Server")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
