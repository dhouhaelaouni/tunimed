"""
Pytest configuration for TuniMed API tests.
Provides fixtures for test database setup and client initialization.
"""

import pytest
import tempfile
import os
from app import create_app
from db import db
from models.user import create_test_users


@pytest.fixture
def app():
    """Create application instance for testing"""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Create Flask app with test configuration
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key-for-testing'
    
    with app.app_context():
        # Create all database tables
        db.create_all()
    
    yield app
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create Flask test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create Flask CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def test_users(app):
    """Create test users in the database"""
    with app.app_context():
        create_test_users()
        
        from models.user import User
        
        # Fetch the created test users
        users = {
            'citizen': User.query.filter_by(username='citizen_test').first(),
            'pharmacist': User.query.filter_by(username='pharmacist_test').first(),
            'regulatory': User.query.filter_by(username='regulatory_test').first(),
            'health_facility': User.query.filter_by(username='healthfacility_test').first(),
            'admin': User.query.filter_by(username='admin').first()
        }
        
        return users


@pytest.fixture
def get_auth_token(client):
    """Fixture to get authentication tokens"""
    def _get_token(username, password):
        response = client.post('/auth/login', json={
            'username': username,
            'password': password
        })
        if response.status_code == 200:
            return response.get_json()['access_token']
        return None
    
    return _get_token
