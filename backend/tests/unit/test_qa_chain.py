import pytest
from app.core.qa_chain import QAChainManager

def test_query_type_detection():
    manager = QAChainManager()
    
    # Test code queries
    assert manager.determine_query_type("create a function") == "code"
    assert manager.determine_query_type("generate class") == "code"
    
    # Test error queries
    assert manager.determine_query_type("fix this error") == "error"
    assert manager.determine_query_type("debug issue") == "error"
    
    # Test general queries
    assert manager.determine_query_type("what is T#?") == "qa"

def test_process_query(mock_vector_store):
    manager = QAChainManager()
    chain = manager.create_qa_chain(mock_vector_store)
    
    # Test valid query
    result = manager.process_query(chain, "test question")
    assert "answer" in result
    assert isinstance(result["answer"], str)
    
    # Test empty query
    result = manager.process_query(chain, "")
    assert "Please provide a valid question" in result["answer"]

def test_memory_management():
    manager = QAChainManager()
    
    # Add messages to memory
    manager.memory.chat_memory.add_user_message("test question")
    manager.memory.chat_memory.add_ai_message("test answer")
    
    # Verify memory
    history = manager.get_chat_history()
    assert len(history) == 2
    
    # Clear memory
    manager.clear_memory()
    assert len(manager.get_chat_history()) == 0