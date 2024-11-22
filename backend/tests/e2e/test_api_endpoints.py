import pytest
from flask.testing import FlaskClient
from app.main import create_app

@pytest.fixture
def client():
    app = create_app(force_recreate=True)
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/api/')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_ask_endpoint(client):
    # Test valid question
    response = client.post('/api/ask', json={'question': 'What is T#?'})
    assert response.status_code == 200
    assert 'answer' in response.json
    
    # Test invalid request
    response = client.post('/api/ask', json={})
    assert response.status_code == 400
    
    # Test missing question
    response = client.post('/api/ask', json={'question': ''})
    assert response.status_code == 400

def test_cors_headers(client):
    response = client.options('/api/ask')
    assert response.status_code == 200
    assert 'Access-Control-Allow-Headers' in response.headers
    assert 'Access-Control-Allow-Methods' in response.headers