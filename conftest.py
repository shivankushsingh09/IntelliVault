"""
Pytest conftest - Shared fixtures for tests
"""
import pytest
import os
import tempfile
from app import create_app
from database.db import init_db
from database.models import db, User

@pytest.fixture(scope='session')
def app():
    """Create application for the test session"""
    app = create_app('testing')
    
    with app.app_context():
        init_db()
        yield app

@pytest.fixture
def client(app):
    """Test client for the app"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """CLI runner for the app"""
    return app.test_cli_runner()

@pytest.fixture
def auth_client(client, app):
    """Authenticated test client"""
    with app.app_context():
        # Create test user
        user = User(
            username='testuser',
            email='test@example.com',
            full_name='Test User'
        )
        user.set_password('TestPass123')
        db.session.add(user)
        db.session.commit()
    
    # Login
    client.post('/auth/api/login', json={
        'username': 'testuser',
        'password': 'TestPass123'
    })
    
    return client
