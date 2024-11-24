import pytest
import json
from app.main import create_app
from contextvars import ContextVar
from werkzeug.test import TestResponse

@pytest.fixture(scope="module")
def app():
    """Create and configure a test Flask application"""
    flask_app = create_app(force_recreate=True)
    flask_app.config['TESTING'] = True
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
            "expected_content": ["T#", "language", "game"],
            "expected_source_contains": ["Basics.md"],
            "min_response_length": 100,
            "should_contain_code": False
        },
        {
            "query": "Show me how to implement player movement with code example",
            "expected_status": 200,
            "expected_content": ["movement", "player", "control"],
            "expected_source_contains": ["Player.md", "Controller"],
            "min_response_length": 200,
            "should_contain_code": True,
            "code_must_contain": ["public class", "void", "movement"]
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
        
        for expected_source in case["expected_source_contains"]:
            assert any(expected_source.lower() in s.lower() for s in sources), \
                f"Expected source '{expected_source}' not found for query: {case['query']}"
        
        # Code block validation
        if case["should_contain_code"]:
            assert "```" in data['answer'], \
                f"Expected code block not found for query: {case['query']}"
            
            if "code_must_contain" in case:
                code_block = data['answer'].split("```")[1]
                for code_element in case["code_must_contain"]:
                    assert code_element.lower() in code_block.lower(), \
                        f"Expected code element '{code_element}' not found for query: {case['query']}"

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