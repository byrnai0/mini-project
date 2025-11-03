from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.file import File
from app.services.abe_service import ABEService

access_bp = Blueprint('access', __name__)

def get_file_model():
    from app import get_db
    return File(get_db())

@access_bp.route('/check-access/<file_id>', methods=['GET'])
@jwt_required()
def check_file_access(file_id):
    """
    Check if current user can access a specific file
    """
    try:
        jwt_data = get_jwt()
        user_attributes = jwt_data.get('attributes', {})
        
        file_model = get_file_model()
        file_record = file_model.get_file_by_id(file_id)
        
        if not file_record:
            return jsonify({'error': 'File not found'}), 404
        
        abe_service = ABEService()
        has_access = abe_service._evaluate_policy(
            user_attributes,
            file_record['encryption_policy']
        )
        
        return jsonify({
            'file_id': file_id,
            'has_access': has_access,
            'required_attributes': file_record['encryption_policy'],
            'user_attributes': user_attributes
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@access_bp.route('/validate-policy', methods=['POST'])
@jwt_required()
def validate_access_policy():
    """
    Validate if a policy is correctly formatted
    Body: {
        "policy": {"role": "manager", "department": "IT"}
    }
    """
    try:
        data = request.get_json()
        policy = data.get('policy', {})
        
        if not isinstance(policy, dict) or not policy:
            return jsonify({
                'valid': False,
                'error': 'Policy must be a non-empty dictionary'
            }), 400
        
        # Basic validation
        allowed_attributes = ['role', 'department', 'clearance', 'team', 'location']
        invalid_attrs = [k for k in policy.keys() if k not in allowed_attributes]
        
        if invalid_attrs:
            return jsonify({
                'valid': False,
                'error': f'Invalid attributes: {invalid_attrs}',
                'allowed_attributes': allowed_attributes
            }), 400
        
        return jsonify({
            'valid': True,
            'policy': policy
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@access_bp.route('/my-attributes', methods=['GET'])
@jwt_required()
def get_my_attributes():
    """Get current user's attributes"""
    try:
        jwt_data = get_jwt()
        user_attributes = jwt_data.get('attributes', {})
        
        return jsonify({
            'attributes': user_attributes
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@access_bp.route('/policy-templates', methods=['GET'])
def get_policy_templates():
    """
    Get common access policy templates
    """
    templates = {
        'executive_only': {
            'role': 'executive',
            'clearance': 5
        },
        'management_team': {
            'role': 'manager',
            'clearance': 3
        },
        'it_department': {
            'department': 'IT'
        },
        'hr_confidential': {
            'department': 'HR',
            'clearance': 4
        },
        'finance_team': {
            'department': 'Finance',
            'role': 'analyst'
        },
        'all_employees': {
            'clearance': 1
        }
    }
    
    return jsonify({'templates': templates}), 200