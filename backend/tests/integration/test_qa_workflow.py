import pytest
from app.core.initializer import initialize_app, AppComponents

@pytest.mark.integration
def test_end_to_end_qa_workflow(test_env):
    # Initialize application
    initialize_app(force_recreate=True)
    
    # Test basic QA workflow
    question = "How do I declare variables in T#?"
    result = AppComponents.qa_chain.invoke({"question": question})
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert "var" in result.lower()

@pytest.mark.integration
def test_error_handling_workflow(test_env):
    # Initialize application
    initialize_app(force_recreate=True)
    
    # Test error handling
    result = AppComponents.qa_chain.invoke({"question": ""})
    assert "Please provide a valid question" in result

@pytest.mark.integration
def test_code_generation_workflow(test_env):
    # Initialize application
    initialize_app(force_recreate=True)
    
    # Test code generation
    question = "Generate code for a player movement system"
    result = AppComponents.qa_chain.invoke({"question": question})
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert "function" in result.lower() or "class" in result.lower()