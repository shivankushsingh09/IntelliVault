"""
IntelliVault Tests
Unit and integration tests for the application
"""
import pytest
import json
from app import create_app
from database.db import init_db
from database.models import User, Note, Document

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    
    with app.app_context():
        init_db()
        yield app

@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """CLI runner"""
    return app.test_cli_runner()

class TestAuth:
    """Test authentication routes"""
    
    def test_register_page(self, client):
        """Test registration page loads"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data
    
    def test_login_page(self, client):
        """Test login page loads"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_register_user(self, client):
        """Test user registration"""
        response = client.post('/auth/api/register', json={
            'full_name': 'Test User',
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123'
        })
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['username'] == 'testuser'
    
    def test_login_user(self, client):
        """Test user login"""
        # Register first
        client.post('/auth/api/register', json={
            'full_name': 'Test User',
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123'
        })
        
        # Login
        response = client.post('/auth/api/login', json={
            'username': 'testuser',
            'password': 'TestPass123'
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['username'] == 'testuser'
    
    def test_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/auth/api/login', json={
            'username': 'nonexistent',
            'password': 'wrongpass'
        })
        assert response.status_code != 200

class TestDashboard:
    """Test dashboard routes"""
    
    def test_dashboard_redirect_unauthenticated(self, client):
        """Test dashboard redirects unauthenticated users"""
        response = client.get('/dashboard', follow_redirects=False)
        assert response.status_code == 302
    
    def test_dashboard_stats_api(self, client):
        """Test dashboard stats API"""
        response = client.get('/api/dashboard/stats')
        assert response.status_code in [200, 302]  # May redirect if not authenticated

class TestNotes:
    """Test notes routes"""
    
    def test_notes_list_page(self, client):
        """Test notes list page"""
        response = client.get('/notes/', follow_redirects=True)
        # May redirect to login or show notes list
        assert response.status_code == 200
    
    def test_create_note_api(self, client):
        """Test creating a note via API"""
        response = client.post('/notes/api/notes', json={
            'title': 'Test Note',
            'content': 'Test content',
            'note_type': 'manual'
        })
        # May return 201 or redirect to login
        assert response.status_code in [201, 302]

class TestSearch:
    """Test search functionality"""
    
    def test_search_page(self, client):
        """Test search page"""
        response = client.get('/search?q=test')
        assert response.status_code in [200, 302]
    
    def test_search_api(self, client):
        """Test search API"""
        response = client.get('/api/search?q=test')
        assert response.status_code in [200, 302]

def test_404_error(client):
    """Test 404 error handling"""
    response = client.get('/nonexistent')
    assert response.status_code == 404

def test_hello_world(client):
    """Test hello world endpoint"""
    response = client.get('/')
    assert response.status_code in [200, 302]

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
