# tests/integration/test_qa_workflow.py

import pytest
import time
from typing import List, Dict, Any
from app.core.initializer import initialize_app, AppComponents

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
def test_end_to_end_qa_workflow(test_env):
    """Test comprehensive QA workflow with various query types"""
    # Initialize application
    initialize_app(force_recreate=True)
    
    # Allow time for initialization
    time.sleep(5)
    
    test_cases = [
        {
            "query": "What is T#? Give me a basic overview.",
            "expected": {
                "content": ["T#", "game", "development", "language"],
                "unwanted": ["undefined", "unknown", "error"],
                "sources": ["T# Basics.md"],
                "min_length": 50,
                "require_code": False
            }
        },
        {
            "query": "How do I implement player movement? Show with code.",
            "expected": {
                "content": [
                    "movement",
                    "player",
                    "transform",
                    "position",
                    "Update",
                    "public class",
                    "StudioBehavior"
                ],
                "sources": [
                    "Working with the Player.md",
                    "Controller.md"
                ],
                "min_length": 100,
                "require_code": True,
                "code_elements": [
                    "transform",
                    "position",
                    "Update",
                    "public class"
                ]
            }
        },
        {
            "query": "What are all the available event functions in T#?",
            "expected": {
                "content": [
                    "Start",
                    "Update",
                    "event",
                    "function",
                    "lifecycle"
                ],
                "sources": ["T# Event Functions.md"],
                "min_length": 75,
                "require_code": True
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
        
        answer = result["answer"].lower()
        
        # Verify content length
        min_length = case["expected"].get("min_length", 50)
        assert len(answer.split()) >= min_length, \
            f"Answer too short for query: {case['query']}"
        
        # Verify expected content
        for content in case["expected"]["content"]:
            combined_text = result["answer"].lower()
            if case["expected"].get("require_code", False):
                code_blocks = result["answer"].split("```")[1::2]
                combined_text += " " + " ".join(code_blocks).lower()
                
            assert content.lower() in combined_text, \
                f"Expected content not found: {content}"
                
        # Verify unwanted content
        for unwanted in case["expected"].get("unwanted", []):
            assert unwanted.lower() not in answer, \
                f"Unwanted content found: {unwanted}"
                
        # Verify sources
        sources = result["sources"]
        for source in case["expected"]["sources"]:
            assert any(source.lower() in s.lower() for s in sources), \
                f"Expected source not found: {source}"
                
        # Verify code elements if required
        if case["expected"].get("require_code", False):
            assert "```" in result["answer"], \
                f"Code block missing for query: {case['query']}"
            
            if "code_elements" in case["expected"]:
                code_blocks = result["answer"].split("```")[1::2]
                code_text = " ".join(code_blocks).lower()
                
                for element in case["expected"]["code_elements"]:
                    assert element.lower() in code_text, \
                        f"Expected code element not found: {element}"

@pytest.mark.integration
def test_error_handling_workflow(test_env):
    """Test error handling with various invalid inputs"""
    initialize_app(force_recreate=True)
    
    error_cases = [
        {
            "query": "",
            "expected_error": "valid question",
            "expected_status": "error"
        },
        {
            "query": " ",
            "expected_error": "valid question", 
            "expected_status": "error"
        },
        {
            "query": "a" * 10000,  # Changed from string to length check
            "expected_error": "length",  # Changed expected error
            "expected_status": "error"
        },
        {
            "query": None,
            "expected_error": "valid question",
            "expected_status": "error"
        },
        {
            "query": ["not", "a", "string"],
            "expected_error": "valid question",
            "expected_status": "error"
        }
    ]
    
    for case in error_cases:
        result = AppComponents.qa_chain_manager.process_query(
            AppComponents.qa_chain,
            case["query"]
        )
        
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "answer" in result, "Result should contain 'answer' field"
        assert any(err in result["answer"].lower() for err in [case["expected_error"], "long"]), \
            f"Expected error message not found for query: {case['query']}"

@pytest.mark.integration
def test_code_generation_workflow(test_env):
    """Test code generation capabilities"""
    initialize_app(force_recreate=True)
    
    code_queries = [
        {
            "query": "Generate code for player movement",
            "expected_elements": {
                "syntax": [
                    "public class",
                    "StudioBehavior",
                    "void Update",
                    "transform.position",
                    "Vector3"
                ],
                "functions": [
                    "GetComponent",
                    "Start",
                    "Update"
                ],
                "patterns": [
                    "private Transform",
                    "caching",
                    "movement",
                    "velocity"
                ],
                "docs": [
                    "Source:",
                    "WARNING:",
                    "Based on:"
                ]
            },
            "required_sections": [
                "SYNTAX REQUIREMENTS",
                "FUNCTION IDENTIFICATION",
                "IMPLEMENTATION",
                "VERIFICATION CHECKLIST"
            ],
            "expected_sources": [
                "Working with the Player.md",
                "T# Event Functions.md",
                "ExampleCode_MountainClimbController.md"
            ],
            "verification_elements": [
                "Documented Elements",
                "Undocumented Elements",
                "Testing Requirements",
                "Integration Notes"
            ]
        },
        {
            "query": "Show me how to implement audio playback",
            "expected_elements": {
                "syntax": [
                    "public class",
                    "StudioBehavior",
                    "AudioSource"
                ],
                "functions": [
                    "PlaySound",
                    "GetComponent",
                    "PlayOneShot"
                ],
                "patterns": [
                    "private AudioSource",
                    "clip",
                    "volume"
                ],
                "docs": [
                    "Source:",
                    "WARNING:",
                    "Based on:"
                ]
            },
            "required_sections": [
                "SYNTAX REQUIREMENTS",
                "FUNCTION IDENTIFICATION",
                "IMPLEMENTATION",
                "VERIFICATION CHECKLIST"
            ],
            "expected_sources": [
                "T# Adding Audio.md",
                "T# Event Functions.md"
            ],
            "verification_elements": [
                "Documented Elements",
                "Undocumented Elements",
                "Testing Requirements",
                "Integration Notes"
            ]
        },
        {
            "query": "Create a coroutine for delayed execution",
            "expected_elements": {
                "syntax": [
                    "public class",
                    "StudioBehavior",
                    "IEnumerator",
                    "yield return"
                ],
                "functions": [
                    "StartCoroutine",
                    "WaitForSeconds",
                    "StopCoroutine"
                ],
                "patterns": [
                    "private IEnumerator",
                    "delay",
                    "coroutine"
                ],
                "docs": [
                    "Source:",
                    "WARNING:",
                    "Based on:"
                ]
            },
            "required_sections": [
                "SYNTAX REQUIREMENTS",
                "FUNCTION IDENTIFICATION",
                "IMPLEMENTATION",
                "VERIFICATION CHECKLIST"
            ],
            "expected_sources": [
                "T# Coroutines.md",
                "T# Event Functions.md"
            ],
            "verification_elements": [
                "Documented Elements",
                "Undocumented Elements",
                "Testing Requirements",
                "Integration Notes"
            ]
        }
    ]
    
    for case in code_queries:
        result = AppComponents.qa_chain_manager.process_query(
            AppComponents.qa_chain,
            case["query"]
        )
        
        # Verify response structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "answer" in result, "Response should contain answer"
        assert "sources" in result, "Response should contain sources"
        
        answer = result["answer"]
        
        # Verify all required sections are present
        for section in case["required_sections"]:
            assert section in answer, f"Missing required section: {section}"
        
        # Verify code block exists
        assert "```" in answer, "No code block found in response"
        
        # Extract code blocks
        code_blocks = answer.split("```")[1::2]
        assert len(code_blocks) > 0, "No code content found in code blocks"
        
        # Verify code content - all elements
        code_content = "\n".join(code_blocks).lower()
        for category, elements in case["expected_elements"].items():
            for element in elements:
                assert element.lower() in code_content or element.lower() in answer.lower(), \
                    f"Expected {category} element '{element}' not found"
                
        # Verify sources
        sources = result["sources"]
        assert isinstance(sources, list), "Sources should be a list"
        assert len(sources) > 0, "No sources provided"
        
        for expected_source in case["expected_sources"]:
            assert any(expected_source.lower() in s.lower() for s in sources), \
                f"Expected source '{expected_source}' not found"
                
        # Verify verification checklist sections
        for verification_element in case["verification_elements"]:
            assert verification_element in answer, \
                f"Missing verification element: {verification_element}"
                
        # Verify documentation patterns
        assert "Source:" in answer, "Missing source documentation in code"
        assert "WARNING:" in answer, "Missing warning documentation for undocumented code"
        
        # Verify code structure
        assert "public class" in code_content, "Missing class definition"
        assert "studiobehavior" in code_content, "Missing StudioBehavior base class"
        
        # Special assertions for each query type
        if "movement" in case["query"].lower():
            assert "transform" in code_content, "Missing transform usage in movement code"
            assert "position" in code_content, "Missing position handling in movement code"
        elif "audio" in case["query"].lower():
            assert "audiosource" in code_content, "Missing AudioSource in audio code"
            assert "playsound" in code_content.lower() or "playoneshot" in code_content.lower(), \
                "Missing audio playback function"
        elif "coroutine" in case["query"].lower():
            assert "ienumerator" in code_content, "Missing IEnumerator in coroutine code"
            assert "yield return" in code_content, "Missing yield return in coroutine code"

def test_code_generation_error_handling(test_env):
    """Test code generation error handling"""
    initialize_app(force_recreate=True)
    
    error_queries = [
        {
            "query": "Generate code for undefined feature",
            "expected_message": "information isn't in the context"
        },
        {
            "query": "Create code without any context",
            "expected_message": "context"
        }
    ]
    
    for case in error_queries:
        result = AppComponents.qa_chain_manager.process_query(
            AppComponents.qa_chain,
            case["query"]
        )
        
        assert isinstance(result, dict)
        assert "answer" in result
        assert case["expected_message"].lower() in result["answer"].lower(), \
            f"Expected error message not found for query: {case['query']}"

def test_code_generation_documentation(test_env):
    """Test code generation documentation requirements"""
    initialize_app(force_recreate=True)
    
    query = "Generate code for player movement"
    result = AppComponents.qa_chain_manager.process_query(
        AppComponents.qa_chain,
        query
    )
    
    answer = result["answer"]
    
    # Verify documentation structure
    assert "SYNTAX REQUIREMENTS" in answer
    assert "FUNCTION IDENTIFICATION" in answer
    assert "IMPLEMENTATION" in answer
    assert "VERIFICATION CHECKLIST" in answer
    
    # Verify source documentation
    assert "Source:" in answer
    assert "WARNING:" in answer
    assert "Based on:" in answer
    
    # Verify checklist completeness
    assert "Documented Elements:" in answer
    assert "Undocumented Elements:" in answer
    assert "Testing Requirements:" in answer
    assert "Integration Notes:" in answer

@pytest.mark.integration
def test_source_documentation_workflow(test_env):
    """Test source documentation and reference handling"""
    initialize_app(force_recreate=True)
    
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