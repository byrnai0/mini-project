from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app.services.blockchain_interface import BlockchainInterface
import hashlib

auth_bp = Blueprint('auth', __name__)

def get_user_model():
    from app import get_db
    return User(get_db())

def get_blockchain_interface():
    return BlockchainInterface()

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register new user
    Body: {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "secure_password",
        "organization": "TechCorp",
        "attributes": {"role": "manager", "department": "IT"}
    }
    """
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['username', 'email', 'password', 'organization', 'attributes']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        user_model = get_user_model()
        
        # Check if user exists
        if user_model.get_user_by_email(data['email']):
            return jsonify({'error': 'User already exists'}), 409
        
        # Hash password
        password_hash = generate_password_hash(data['password'])
        
        # Register user on blockchain (interface to blockchain team)
        blockchain = get_blockchain_interface()
        attributes_hash = hashlib.sha256(
            str(data['attributes']).encode()
        ).hexdigest()
        
        blockchain_result = blockchain.register_user_on_chain(
            data['email'], 
            attributes_hash
        )
        
        # Create user in database
        user_data = {
            'username': data['username'],
            'email': data['email'],
            'password_hash': password_hash,
            'organization': data['organization'],
            'attributes': data['attributes'],
            'bcid': blockchain_result['bcid']
        }
        
        user_id = user_model.create_user(user_data)
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id,
            'bcid': blockchain_result['bcid'],
            'tx_hash': blockchain_result['tx_hash']
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login
    Body: {
        "email": "john@example.com",
        "password": "secure_password"
    }
    """
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        user_model = get_user_model()
        user = user_model.get_user_by_email(data['email'])
        
        if not user or not check_password_hash(user['password_hash'], data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create JWT token
        access_token = create_access_token(
            identity=str(user['_id']),
            additional_claims={
                'bcid': user.get('bcid'),
                'attributes': user.get('attributes', {})
            }
        )
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'bcid': user.get('bcid'),
                'attributes': user.get('attributes')
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        user_model = get_user_model()
        user = user_model.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'organization': user['organization'],
                'attributes': user.get('attributes'),
                'bcid': user.get('bcid')
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500