import pytest
import time
from typing import List, Dict, Any
from app.core.initializer import initialize_app, AppComponents, shutdown_app


@pytest.fixture(autouse=True)
def setup_and_cleanup():
    """Fixture to handle setup and cleanup for each test"""
    try:
        # Initialize dependencies
        initialize_app(force_recreate=True)
        time.sleep(5)  # Allow time for initialization
        yield
    finally:
        shutdown_app()
        time.sleep(1)  # Allow time for cleanup

def verify_qa_response(response: Dict[str, Any], expected: Dict[str, Any]) -> List[str]:
    """Helper function to verify QA response with detailed checks"""
    errors = []
    
    # Check basic response structure
    if not isinstance(response, dict):
        errors.append(f"Response should be dict, got {type(response)}")
        return errors
        
    # Check required fields
    for field in ['answer', 'sources']:
        if field not in response:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return errors
        
    # Verify answer content
    answer = response['answer'].lower()
    
    # Check for expected content
    for content in expected.get('expected_content', []):
        if content.lower() not in answer:
            errors.append(f"Expected content not found: {content}")
            
    # Check for unwanted content
    for content in expected.get('unwanted_content', []):
        if content.lower() in answer:
            errors.append(f"Unwanted content found: {content}")
    
    # Verify minimum length
    min_length = expected.get('min_length', 50)
    if len(answer.split()) < min_length:
        errors.append(f"Answer too short. Expected at least {min_length} words")
    
    # Verify sources
    sources = response['sources']
    if not isinstance(sources, list):
        errors.append("Sources should be a list")
    else:
        # Check expected source documents
        for source in expected.get('expected_sources', []):
            if not any(source.lower() in s.lower() for s in sources):
                errors.append(f"Expected source not found: {source}")
    
    # Check code blocks if required
    if expected.get('should_have_code', False):
        if '```' not in response['answer']:
            errors.append("Expected code block not found")
        else:
            code_blocks = response['answer'].split('```')[1::2]  # Get code blocks
            for block in code_blocks:
                # Check for code indicators
                if not any(indicator in block.lower() for indicator in 
                         ['class', 'function', 'void', 'public', 'private']):
                    errors.append("Code block doesn't appear to contain valid code")
                    
    return errors

@pytest.mark.integration
def test_end_to_end_qa_workflow():
    """Test that the basic QA workflow functions properly"""
    test_cases = [
        {
            "query": "What is T#?",
            "expected_format": {
                "has_answer": True,
                "has_sources": True,
                "min_length": 50  # Just to ensure we got a real response
            }
        },
        {
            "query": "How do I implement player movement?",
            "expected_format": {
                "has_answer": True,
                "has_sources": True,
                "has_code": True  # Since this is a code question
            }
        }
    ]
    
    for case in test_cases:
        # Process query
        result = AppComponents.qa_chain_manager.process_query(
            AppComponents.qa_chain,
            case["query"]
        )

        # Verify response structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "answer" in result, "Response should contain answer"
        assert "sources" in result, "Response should contain sources"
        
        # Verify basic format expectations
        if case["expected_format"].get("has_answer"):
            assert len(result["answer"]) > 0, "Answer should not be empty"
            
        if case["expected_format"].get("min_length"):
            assert len(result["answer"].split()) >= case["expected_format"]["min_length"], \
                "Answer should meet minimum length requirement"
                
        if case["expected_format"].get("has_sources"):
            assert isinstance(result["sources"], list), "Sources should be a list"
            assert len(result["sources"]) > 0, "Should have at least one source"
            
        if case["expected_format"].get("has_code"):
            assert "```" in result["answer"], "Code question should include code block"

@pytest.mark.integration
def test_error_handling_workflow():
    """Test that error handling works properly for invalid queries"""
    error_cases = [
        {
            "query": "",
            "should_contain": "provide a valid question"
        },
        {
            "query": "   ",
            "should_contain": "provide a valid question"
        },
        {
            "query": "tell me about quantum physics and baking cookies together",
            "should_contain": "information isn't in the context"
        }
    ]
    
    for case in error_cases:
        result = AppComponents.qa_chain_manager.process_query(
            AppComponents.qa_chain,
            case["query"]
        )
        
        assert isinstance(result, dict)
        assert "answer" in result
        assert case["should_contain"].lower() in result["answer"].lower()

@pytest.mark.integration
def test_code_generation_workflow():
    """Test basic code generation structure"""
    query = "Generate code for player movement"
    result = AppComponents.qa_chain_manager.process_query(
        AppComponents.qa_chain,
        query
    )
    
    # Verify response structure
    assert isinstance(result, dict)
    assert "answer" in result
    assert "```" in result["answer"], "No code block found in response"
    
    # Extract code block and verify C# syntax markers
    code_blocks = result["answer"].split("```")
    assert len(code_blocks) > 1, "No proper code block markers found"
    code_content = code_blocks[1]  # Get content between first pair of ```
    
    # Verify basic C# syntax elements
    basic_syntax_elements = [
        "class",
        "public",
        "{",
        "}"
    ]
    
    for element in basic_syntax_elements:
        assert element in code_content, f"Missing basic C# syntax element: {element}"

@pytest.mark.integration
def test_code_generation_error_handling():
    """Test handling of requests for non-existent features"""
    query = "Generate code for quantum teleportation using blockchain AI in T#"
    result = AppComponents.qa_chain_manager.process_query(
        AppComponents.qa_chain,
        query
    )
    
    assert isinstance(result, dict)
    assert "answer" in result
    # Check if response indicates information is not in documentation
    assert any(phrase in result["answer"].lower() for phrase in [
        "isn't in the context",
        "not found in the documentation",
        "no documentation available"
    ])

@pytest.mark.integration
def test_code_generation_documentation():
    """Test that generated code includes comments"""
    query = "Generate code for player movement"
    result = AppComponents.qa_chain_manager.process_query(
        AppComponents.qa_chain,
        query
    )
    
    assert isinstance(result, dict)
    assert "answer" in result
    
    # Extract code block
    code_blocks = result["answer"].split("```")
    assert len(code_blocks) > 1, "No code block found"
    code_content = code_blocks[1]
    
    # Verify presence of comments (not specific content)
    comment_indicators = [
        "//",  # Single line comments
        "/*",  # Multi-line comments start
        "*/"   # Multi-line comments end
    ]
    
    has_comments = any(indicator in code_content for indicator in comment_indicators)
    assert has_comments, "No comments found in generated code"

@pytest.mark.integration
def test_source_documentation_workflow():
    """Test source documentation and reference handling"""
    result = AppComponents.qa_chain_manager.process_query(
        AppComponents.qa_chain,
        "What are all the available features in T#?"
    )
    
    # Verify sources
    assert "sources" in result
    sources = result["sources"]
    assert isinstance(sources, list)
    assert len(sources) > 0
    assert all(isinstance(s, str) for s in sources)
    assert all(s.endswith('.md') for s in sources)
    
    # Verify source diversity
    unique_sources = set(sources)
    assert len(unique_sources) > 1, "Response should reference multiple source documents"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--log-cli-level=INFO"])