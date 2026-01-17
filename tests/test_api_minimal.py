"""
Minimal pytest test suite for TuniMed API.
Tests user authentication and medicine declaration functionality.
"""

import pytest
import json
from datetime import datetime, timedelta
from models.user import User, Medicine


class TestUserAuthentication:
    """Tests for user authentication endpoints"""
    
    def test_register_new_user(self, client):
        """Test user registration with valid data"""
        response = client.post('/auth/register', json={
            'username': 'new_user',
            'email': 'newuser@test.com',
            'password': 'securepass123',
            'role': 'CITIZEN'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'User registered successfully'
        assert data['user']['username'] == 'new_user'
        assert data['user']['role'] == 'CITIZEN'
    
    def test_register_missing_required_fields(self, client):
        """Test registration fails with missing required fields"""
        response = client.post('/auth/register', json={
            'username': 'new_user',
            'email': 'newuser@test.com'
            # password is missing
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error_code'] == 'missing_required_fields'
    
    def test_register_invalid_role(self, client):
        """Test registration fails with invalid role"""
        response = client.post('/auth/register', json={
            'username': 'new_user',
            'email': 'newuser@test.com',
            'password': 'securepass123',
            'role': 'INVALID_ROLE'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error_code'] == 'invalid_role'
    
    def test_register_duplicate_username(self, client, test_users):
        """Test registration fails with duplicate username"""
        response = client.post('/auth/register', json={
            'username': 'citizen_test',  # Already exists
            'email': 'different@test.com',
            'password': 'securepass123'
        })
        
        assert response.status_code == 409
        data = response.get_json()
        assert data['error_code'] == 'user_exists'
    
    def test_login_success(self, client, test_users):
        """Test successful user login"""
        response = client.post('/auth/login', json={
            'username': 'citizen_test',
            'password': 'citizenpass'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['username'] == 'citizen_test'
        assert data['user']['role'] == 'CITIZEN'
    
    def test_login_invalid_password(self, client, test_users):
        """Test login fails with invalid password"""
        response = client.post('/auth/login', json={
            'username': 'citizen_test',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['error_code'] == 'authentication_failed'
    
    def test_login_user_not_found(self, client):
        """Test login fails for non-existent user"""
        response = client.post('/auth/login', json={
            'username': 'nonexistent_user',
            'password': 'anypassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['error_code'] == 'authentication_failed'
    
    def test_get_current_user(self, client, test_users, get_auth_token):
        """Test getting current user information"""
        token = get_auth_token('citizen_test', 'citizenpass')
        assert token is not None
        
        response = client.get('/auth/me', headers={
            'Authorization': f'Bearer {token}'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['username'] == 'citizen_test'
        assert data['user']['id'] is not None
    
    def test_get_current_user_without_token(self, client):
        """Test getting current user fails without token"""
        response = client.get('/auth/me')
        
        assert response.status_code == 401


class TestMedicineDeclaration:
    """Tests for medicine declaration functionality"""
    
    def test_declare_medicine_success(self, client, test_users, get_auth_token):
        """Test successful medicine declaration"""
        token = get_auth_token('citizen_test', 'citizenpass')
        
        tomorrow = datetime.utcnow() + timedelta(days=30)
        response = client.post('/medicines/declarations', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'name': 'Aspirin',
                'amm': 'AMM12345',
                'batch_number': 'BATCH001',
                'expiration_date': tomorrow.isoformat(),
                'quantity': 10,
                'is_imported': False
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Medicine declared successfully'
        assert data['medicine']['name'] == 'Aspirin'
        assert data['medicine']['status'] == 'SUBMITTED'
        assert data['medicine']['quantity'] == 10
    
    def test_declare_medicine_missing_required_fields(self, client, test_users, get_auth_token):
        """Test medicine declaration fails with missing required fields"""
        token = get_auth_token('citizen_test', 'citizenpass')
        
        response = client.post('/medicines/declarations',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'name': 'Aspirin',
                'amm': 'AMM12345'
                # Missing batch_number, expiration_date, quantity
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error_code'] == 'missing_required_fields'
    
    def test_declare_medicine_expired_date(self, client, test_users, get_auth_token):
        """Test medicine declaration fails with expired date"""
        token = get_auth_token('citizen_test', 'citizenpass')
        
        yesterday = datetime.utcnow() - timedelta(days=1)
        response = client.post('/medicines/declarations',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'name': 'Aspirin',
                'amm': 'AMM12345',
                'batch_number': 'BATCH001',
                'expiration_date': yesterday.isoformat(),
                'quantity': 10
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error_code'] == 'expired_date'
    
    def test_declare_medicine_invalid_quantity(self, client, test_users, get_auth_token):
        """Test medicine declaration fails with invalid quantity"""
        token = get_auth_token('citizen_test', 'citizenpass')
        
        tomorrow = datetime.utcnow() + timedelta(days=30)
        response = client.post('/medicines/declarations',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'name': 'Aspirin',
                'amm': 'AMM12345',
                'batch_number': 'BATCH001',
                'expiration_date': tomorrow.isoformat(),
                'quantity': 0  # Invalid: must be > 0
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error_code'] == 'integer_below_minimum'
    
    def test_declare_medicine_invalid_quantity_type(self, client, test_users, get_auth_token):
        """Test medicine declaration fails with invalid quantity type"""
        token = get_auth_token('citizen_test', 'citizenpass')
        
        tomorrow = datetime.utcnow() + timedelta(days=30)
        response = client.post('/medicines/declarations',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'name': 'Aspirin',
                'amm': 'AMM12345',
                'batch_number': 'BATCH001',
                'expiration_date': tomorrow.isoformat(),
                'quantity': 'not_a_number'
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error_code'] == 'invalid_integer_type'
    
    def test_declare_medicine_without_authentication(self, client):
        """Test medicine declaration requires authentication"""
        tomorrow = datetime.utcnow() + timedelta(days=30)
        response = client.post('/medicines/declarations',
            json={
                'name': 'Aspirin',
                'amm': 'AMM12345',
                'batch_number': 'BATCH001',
                'expiration_date': tomorrow.isoformat(),
                'quantity': 10
            }
        )
        
        assert response.status_code == 401
    
    def test_declare_medicine_non_citizen_role(self, client, test_users, get_auth_token):
        """Test medicine declaration only allowed for CITIZEN role"""
        token = get_auth_token('pharmacist_test', 'pharmacistpass')
        
        tomorrow = datetime.utcnow() + timedelta(days=30)
        response = client.post('/medicines/declarations',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'name': 'Aspirin',
                'amm': 'AMM12345',
                'batch_number': 'BATCH001',
                'expiration_date': tomorrow.isoformat(),
                'quantity': 10
            }
        )
        
        assert response.status_code == 403
    
    def test_get_my_declarations(self, client, test_users, get_auth_token):
        """Test getting user's own medicine declarations"""
        token = get_auth_token('citizen_test', 'citizenpass')
        
        # First, declare a medicine
        tomorrow = datetime.utcnow() + timedelta(days=30)
        client.post('/medicines/declarations',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'name': 'Aspirin',
                'amm': 'AMM12345',
                'batch_number': 'BATCH001',
                'expiration_date': tomorrow.isoformat(),
                'quantity': 10
            }
        )
        
        # Now get all declarations
        response = client.get('/medicines/declarations/my',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] >= 1
        assert len(data['medicines']) >= 1
        assert data['medicines'][0]['name'] == 'Aspirin'
