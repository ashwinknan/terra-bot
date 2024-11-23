import pytest
from unittest.mock import Mock, patch, MagicMock
from app.core.qa_chain import QAChainManager
from langchain_core.messages import HumanMessage, AIMessage

@pytest.fixture
def mock_llm():
    llm = MagicMock()
    llm.invoke.return_value = "Test response"
    return llm

@pytest.fixture
def mock_retriever():
    retriever = MagicMock()
    retriever.get_relevant_documents.return_value = []
    return retriever

@pytest.fixture
def qa_manager(mock_llm, mock_retriever):
    with patch('app.core.qa_chain.ChatAnthropic', return_value=mock_llm):
        manager = QAChainManager()
        manager.retriever = mock_retriever
        return manager

def test_query_type_detection(qa_manager):
    """Test query type detection with various inputs"""
    test_cases = [
        ("create a function", "code"),
        ("generate class", "code"),
        ("write a method", "code"),
        ("fix this error", "error"),
        ("debug issue", "error"),
        ("null reference", "error"),
        ("what is T#?", "qa"),
        ("explain how", "qa"),
    ]

    for query, expected_type in test_cases:
        assert qa_manager.determine_query_type(query) == expected_type

def test_process_query_validation(qa_manager):
    """Test query input validation"""
    invalid_inputs = [
        None,
        "",
        " ",
        ["not a string"],
        123,
        {"not": "string"},
    ]

    for invalid_input in invalid_inputs:
        result = qa_manager.process_query(qa_manager.qa_chain, invalid_input)
        assert "Please provide a valid question" in result["answer"]
        assert isinstance(result["sources"], list)
        assert len(result["sources"]) == 0

@patch('app.core.qa_chain.RunnablePassthrough')
def test_chain_creation(mock_runnable, qa_manager, mock_retriever):
    """Test QA chain creation"""
    mock_vector_store = MagicMock()
    mock_vector_store.as_retriever.return_value = mock_retriever

    chain = qa_manager.create_qa_chain(mock_vector_store)
    assert chain is not None
    assert hasattr(qa_manager, 'qa_chain')
    assert hasattr(qa_manager, 'code_chain')
    assert hasattr(qa_manager, 'error_chain')

def test_memory_management(qa_manager):
    """Test conversation memory management"""
    # Add messages
    test_messages = [
        ("user question", "ai response"),
        ("another question", "another response"),
    ]

    for user_msg, ai_msg in test_messages:
        qa_manager.memory.chat_memory.add_user_message(user_msg)
        qa_manager.memory.chat_memory.add_ai_message(ai_msg)

    # Verify memory
    history = qa_manager.get_chat_history()
    assert len(history) == len(test_messages) * 2  # Both user and AI messages
    assert isinstance(history[0], HumanMessage)
    assert isinstance(history[1], AIMessage)

    # Test memory clearing
    qa_manager.clear_memory()
    assert len(qa_manager.get_chat_history()) == 0

@patch('app.config.prompt_templates.PROMPT_TEMPLATES')
def test_specialized_chains(mock_templates, qa_manager):
    """Test specialized chain selection and execution"""
    test_cases = [
        ("write code for player movement", "code_chain"),
        ("fix this null reference error", "error_chain"),
        ("what is the syntax for loops", "qa_chain"),
    ]

    for query, expected_chain in test_cases:
        with patch.object(qa_manager, expected_chain) as mock_chain:
            mock_chain.invoke.return_value = "Test response"
            result = qa_manager.process_query(qa_manager.qa_chain, query)
            assert mock_chain.invoke.called
            assert isinstance(result["answer"], str)
            assert "sources" in result