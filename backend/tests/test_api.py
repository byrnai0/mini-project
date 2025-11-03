import pytest
import json
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_register_user(client):
    """Test user registration"""
    data = {
        'username': 'test_user',
        'email': 'test@example.com',
        'password': 'SecurePass123',
        'organization': 'TestOrg',
        'attributes': {'role': 'manager', 'department': 'IT'}
    }
    
    response = client.post(
        '/api/auth/register',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    assert 'bcid' in response.json

def test_login(client):
    """Test user login"""
    # First register
    register_data = {
        'username': 'login_test',
        'email': 'login@example.com',
        'password': 'SecurePass123',
        'organization': 'TestOrg',
        'attributes': {'role': 'employee'}
    }
    client.post('/api/auth/register', json=register_data)
    
    # Then login
    login_data = {
        'email': 'login@example.com',
        'password': 'SecurePass123'
    }
    
    response = client.post('/api/auth/login', json=login_data)
    
    assert response.status_code == 200
    assert 'access_token' in response.json