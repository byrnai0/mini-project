import pytest
from app.services.abe_service import ABEService

def test_encrypt_decrypt_success():
    """Test successful encryption and decryption"""
    abe = ABEService()
    
    # Test data
    file_data = b"This is sensitive data"
    policy = {'role': 'manager', 'department': 'IT'}
    user_attributes = {'role': 'manager', 'department': 'IT'}
    
    # Encrypt
    encrypted = abe.encrypt_file(file_data, policy)
    
    assert 'encrypted_data' in encrypted
    assert 'encrypted_key' in encrypted
    assert 'policy' in encrypted
    
    # Decrypt
    decrypted = abe.decrypt_file(
        encrypted['encrypted_data'],
        encrypted['encrypted_key'],
        user_attributes,
        policy
    )
    
    assert decrypted == file_data

def test_decrypt_with_wrong_attributes():
    """Test decryption fails with wrong attributes"""
    abe = ABEService()
    
    file_data = b"Sensitive data"
    policy = {'role': 'manager', 'clearance': 5}
    wrong_attributes = {'role': 'employee', 'clearance': 2}
    
    encrypted = abe.encrypt_file(file_data, policy)
    
    with pytest.raises(PermissionError):
        abe.decrypt_file(
            encrypted['encrypted_data'],
            encrypted['encrypted_key'],
            wrong_attributes,
            policy
        )

def test_policy_evaluation():
    """Test access policy evaluation"""
    abe = ABEService()
    
    # Should pass
    assert abe._evaluate_policy(
        {'role': 'manager', 'department': 'IT'},
        {'role': 'manager'}
    ) == True
    
    # Should fail
    assert abe._evaluate_policy(
        {'role': 'employee'},
        {'role': 'manager'}
    ) == False