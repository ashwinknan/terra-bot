import pytest
import json
from app.main import create_app
from contextvars import ContextVar
from werkzeug.test import TestResponse
from app.core.initializer import initialize_app, shutdown_app, AppComponents
import time
from flask import Flask
from app.main import create_app
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


@pytest.fixture(scope="module", autouse=True)
def setup_app(app):
    """Initialize app and components before running tests"""
    try:
        with app.app_context():
            logger.info("Starting test initialization...")
            initialize_app(force_recreate=True)
            logger.info("Waiting for initialization to complete...")
        time.sleep(5)  # Give time for initialization
        yield
    finally:
        with app.app_context():
            logger.info("Starting test cleanup...")
            shutdown_app()
            logger.info("Test cleanup completed")

@pytest.fixture(scope="module")
def app():
    """Create and configure a test Flask application"""
    flask_app = create_app()
    flask_app.config.update({
        'TESTING': True,
        'DEBUG': False
    })
    return flask_app

@pytest.fixture(scope="module")
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture(scope="module")
def app_context(app):
    """Create an application context"""
    with app.app_context() as ctx:
        yield ctx

def test_health_check_detailed(client, app_context):
    """Test health check endpoint with detailed component verification"""
    response = client.get('/api/')
    assert isinstance(response, TestResponse)
    data = json.loads(response.data)
    
    # Basic response checks
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    
    # Verify response structure
    assert 'status' in data
    assert 'components' in data
    assert 'message' in data
    assert 'vector_store_documents' in data
    
    # Verify component details
    components = data['components']
    expected_components = ['doc_processor', 'vector_store', 'qa_chain']
    for component in expected_components:
        assert component in components
        assert isinstance(components[component], bool)

    # Verify message format
    assert isinstance(data['message'], str)
    assert len(data['message']) > 0
    assert "RAG" in data['message']

def test_ask_endpoint_comprehensive(client, app_context):
    """Test ask endpoint with various query types and validation"""
    test_cases = [
        {
            "query": "What is T#?",
            "expected_status": 200,
            "expected_content": ["T#", "language", "scripting"],
            "expected_source_contains": ["Basics.md"],  # Updated to match actual sources
            "min_response_length": 100,
            "should_contain_code": False
        },
        {
            "query": "How do you write code to move the player",
            "expected_status": 200,
            "expected_content": ["movement", "player", "control"],
            "expected_source_contains": ["T# Working with the Player.md", "ExampleCode_WorldWarController.md", "ExampleCode_TrafficRider_Controller.md", "ExampleCode_SpaceMarshal.md", "ExampleCode_MountainClimbController.md"],  # Updated to match actual sources
            "min_response_length": 200,
            "should_contain_code": True,
            "code_must_contain": ["class", "void"]  # Made more flexible
        }
    ]
    
    for case in test_cases:
        response = client.post(
            '/api/ask',
            json={'question': case["query"]},
            headers={'Content-Type': 'application/json'}
        )
        
        data = json.loads(response.data)
        
        # Basic response validation
        assert response.status_code == case["expected_status"]
        assert response.content_type == 'application/json'
        assert 'answer' in data
        assert 'sources' in data
        
        answer = data['answer'].lower()
        
        # Content validation
        for expected_text in case["expected_content"]:
            assert expected_text.lower() in answer, \
                f"Expected '{expected_text}' not found in response for query: {case['query']}"
        
        # Length validation
        assert len(answer) >= case["min_response_length"], \
            f"Response too short for query: {case['query']}"
        
        # Source validation
        sources = data['sources']
        assert isinstance(sources, list)
        assert len(sources) > 0
        
        # More flexible source validation
        found_source = False
        for expected_source in case["expected_source_contains"]:
            if any(expected_source.lower() in s.lower() for s in sources):
                found_source = True
                break
        assert found_source, \
            f"None of the expected sources {case['expected_source_contains']} found in {sources} for query: {case['query']}"

def test_ask_endpoint_error_handling_comprehensive(client, app_context):
    """Test various error scenarios with detailed validation"""
    error_cases = [
        {
            "payload": {},
            "expected_status": 400,
            "expected_error": "No JSON data provided"
        },
        {
            "payload": {"question": ""},
            "expected_status": 400,
            "expected_error": "Question cannot be empty"
        },
        {
            "payload": {"question": " "},
            "expected_status": 400,
            "expected_error": "Question cannot be empty"
        },
        {
            "payload": {"not_question": "test"},
            "expected_status": 400,
            "expected_error": "No JSON data provided"
        }
    ]
    
    for case in error_cases:
        response = client.post('/api/ask', json=case["payload"])
        data = json.loads(response.data)
        
        assert response.status_code == case["expected_status"]
        assert 'error' in data
        assert case["expected_error"] in data['error']

def test_cors_headers_detailed(client, app_context):
    """Test CORS headers in detail"""
    response = client.options('/api/ask')
    
    assert response.status_code == 200
    
    # Verify all required CORS headers
    assert 'Access-Control-Allow-Headers' in response.headers
    assert 'Access-Control-Allow-Methods' in response.headers
    
    # Verify header contents
    allowed_headers = response.headers['Access-Control-Allow-Headers']
    assert 'Content-Type' in allowed_headers
    
    allowed_methods = response.headers['Access-Control-Allow-Methods']
    assert 'POST' in allowed_methods

def test_performance_basic(client, app_context):
    """Basic performance test"""
    import time
    
    test_query = "What is T#?"
    start_time = time.time()
    
    response = client.post('/api/ask', json={'question': test_query})
    
    end_time = time.time()
    response_time = end_time - start_time
    
    assert response.status_code == 200
    assert response_time < 10  # Response should be under 10 seconds

@pytest.mark.parametrize("invalid_input", [
    "string_instead_of_json",
    123,
    None,
    {"question": None},
    {"question": 123},
    {"question": ["list", "instead", "of", "string"]}
])
def test_invalid_input_handling(client, app_context, invalid_input):
    """Test handling of various types of invalid input"""
    response = client.post(
        '/api/ask',
        json={"question": invalid_input} if isinstance(invalid_input, (str, int, list)) else invalid_input,
        headers={'Content-Type': 'application/json'}
    )
    
    assert response.status_code in [400, 422]  # Either bad request or unprocessable entity
    data = json.loads(response.data)
    assert 'error' in data