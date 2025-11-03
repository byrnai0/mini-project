from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.utils import secure_filename
from app.models.file import File
from app.models.user import User
from app.services.abe_service import ABEService
from app.services.ipfs_service import IPFSService
from app.services.blockchain_interface import BlockchainInterface
import hashlib
import io

files_bp = Blueprint('files', __name__)

def get_file_model():
    from app import get_db
    return File(get_db())

def get_user_model():
    from app import get_db
    return User(get_db())

@files_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """
    Upload and encrypt file
    Form Data:
        - file: file object
        - access_policy: JSON string {"role": "manager", "department": "IT"}
    """
    try:
        user_id = get_jwt_identity()
        jwt_data = get_jwt()
        user_bcid = jwt_data.get('bcid')
        
        # Check if file exists in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get access policy
        access_policy_str = request.form.get('access_policy', '{}')
        import json
        access_policy = json.loads(access_policy_str)
        
        if not access_policy:
            return jsonify({'error': 'Access policy required'}), 400
        
        # Read file data
        file_data = file.read()
        original_filename = secure_filename(file.filename)
        
        # Initialize services
        abe_service = ABEService()
        ipfs_service = IPFSService()
        blockchain = BlockchainInterface()
        
        # Step 1: Encrypt file with ABE
        encrypted_result = abe_service.encrypt_file(file_data, access_policy)
        
        # Step 2: Upload encrypted file to IPFS
        ipfs_cid = ipfs_service.upload_file(
            encrypted_result['encrypted_data'], 
            original_filename
        )
        
        # Pin file for persistence
        ipfs_service.pin_file(ipfs_cid)
        
        # Step 3: Register CID on blockchain
        metadata_hash = hashlib.sha256(
            f"{ipfs_cid}{original_filename}".encode()
        ).hexdigest()
        
        blockchain_result = blockchain.register_file_cid_on_chain(
            user_bcid,
            ipfs_cid,
            metadata_hash
        )
        
        # Step 4: Store metadata in database
        file_model = get_file_model()
        file_record = {
            'filename': original_filename,
            'original_filename': original_filename,
            'file_size': len(file_data),
            'file_type': file.content_type,
            'owner_id': user_id,
            'ipfs_cid': ipfs_cid,
            'encryption_policy': access_policy,
            'encrypted_key': encrypted_result['encrypted_key'],
            'blockchain_tx_hash': blockchain_result['tx_hash'],
            'is_encrypted': True
        }
        
        file_id = file_model.create_file_record(file_record)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file_id': file_id,
            'ipfs_cid': ipfs_cid,
            'blockchain_tx_hash': blockchain_result['tx_hash'],
            'access_policy': access_policy
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@files_bp.route('/download/<file_id>', methods=['GET'])
@jwt_required()
def download_file(file_id):
    """
    Download and decrypt file (if user has access)
    """
    try:
        user_id = get_jwt_identity()
        jwt_data = get_jwt()
        user_attributes = jwt_data.get('attributes', {})
        
        # Get file metadata
        file_model = get_file_model()
        file_record = file_model.get_file_by_id(file_id)
        
        if not file_record:
            return jsonify({'error': 'File not found'}), 404
        
        # Initialize services
        abe_service = ABEService()
        ipfs_service = IPFSService()
        
        # Step 1: Check access policy
        if not abe_service._evaluate_policy(user_attributes, file_record['encryption_policy']):
            return jsonify({'error': 'Access denied: Insufficient permissions'}), 403
        
        # Step 2: Retrieve encrypted file from IPFS
        encrypted_data = ipfs_service.get_file(file_record['ipfs_cid'])
        
        # Step 3: Decrypt file
        decrypted_data = abe_service.decrypt_file(
            encrypted_data,
            file_record['encrypted_key'],
            user_attributes,
            file_record['encryption_policy']
        )
        
        # Step 4: Increment access count
        file_model.increment_access_count(file_id)
        
        # Return file
        return send_file(
            io.BytesIO(decrypted_data),
            as_attachment=True,
            download_name=file_record['original_filename']
        )
        
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@files_bp.route('/my-files', methods=['GET'])
@jwt_required()
def get_my_files():
    """Get all files owned by current user"""
    try:
        user_id = get_jwt_identity()
        file_model = get_file_model()
        files = file_model.get_files_by_owner(user_id)
        
        file_list = []
        for file in files:
            file_list.append({
                'id': str(file['_id']),
                'filename': file['filename'],
                'file_size': file['file_size'],
                'file_type': file['file_type'],
                'ipfs_cid': file['ipfs_cid'],
                'access_policy': file['encryption_policy'],
                'created_at': file['created_at'].isoformat(),
                'access_count': file.get('access_count', 0)
            })
        
        return jsonify({'files': file_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@files_bp.route('/shared-files', methods=['GET'])
@jwt_required()
def get_shared_files():
    """Get all files user has access to"""
    try:
        jwt_data = get_jwt()
        user_attributes = jwt_data.get('attributes', {})
        
        file_model = get_file_model()
        abe_service = ABEService()
        
        # Get all files
        all_files = file_model.get_shared_files(user_attributes)
        
        # Filter files based on access policy
        accessible_files = []
        for file in all_files:
            if abe_service._evaluate_policy(user_attributes, file['encryption_policy']):
                accessible_files.append({
                    'id': str(file['_id']),
                    'filename': file['filename'],
                    'file_size': file['file_size'],
                    'file_type': file['file_type'],
                    'created_at': file['created_at'].isoformat(),
                    'owner_id': file['owner_id']
                })
            return jsonify({'files': accessible_files}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@files_bp.route('/file/<file_id>/info', methods=['GET'])
@jwt_required()
def get_file_info(file_id):
    """Get file metadata without downloading"""
    try:
        user_id = get_jwt_identity()
        jwt_data = get_jwt()
        user_attributes = jwt_data.get('attributes', {})
        
        file_model = get_file_model()
        file_record = file_model.get_file_by_id(file_id)
        
        if not file_record:
            return jsonify({'error': 'File not found'}), 404
        
        # Check if user can access this file
        abe_service = ABEService()
        has_access = abe_service._evaluate_policy(
            user_attributes, 
            file_record['encryption_policy']
        )
        
        return jsonify({
            'file': {
                'id': str(file_record['_id']),
                'filename': file_record['filename'],
                'file_size': file_record['file_size'],
                'file_type': file_record['file_type'],
                'ipfs_cid': file_record['ipfs_cid'],
                'access_policy': file_record['encryption_policy'],
                'created_at': file_record['created_at'].isoformat(),
                'access_count': file_record.get('access_count', 0),
                'blockchain_tx': file_record.get('blockchain_tx_hash'),
                'has_access': has_access
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@files_bp.route('/file/<file_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """Soft delete file (only owner can delete)"""
    try:
        user_id = get_jwt_identity()
        file_model = get_file_model()
        file_record = file_model.get_file_by_id(file_id)
        
        if not file_record:
            return jsonify({'error': 'File not found'}), 404
        
        # Check if user is owner
        if file_record['owner_id'] != user_id:
            return jsonify({'error': 'Only file owner can delete'}), 403
        
        # Soft delete (mark as inactive)
        file_model.collection.update_one(
            {'_id': file_record['_id']},
            {'$set': {'is_active': False}}
        )
        
        # Optionally unpin from IPFS
        ipfs_service = IPFSService()
        ipfs_service.unpin_file(file_record['ipfs_cid'])
        
        return jsonify({'message': 'File deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500