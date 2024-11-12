# tests/unit/test_qa_chain.py
import pytest
from unittest.mock import MagicMock, create_autospec, patch
import logging
from langchain_core.retrievers import BaseRetriever
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage
from app.core.qa_chain import QAChainManager
from app.config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def qa_manager():
    """Create a QA chain manager instance"""
    return QAChainManager()

@pytest.fixture
def mock_vector_store():
    """Create a properly configured mock vector store"""
    # Create a mock retriever that inherits from BaseRetriever
    mock_retriever = create_autospec(BaseRetriever)
    
    # Configure the mock vector store
    mock_store = MagicMock(spec=Chroma)
    mock_store.as_retriever.return_value = mock_retriever
    
    # Configure the retriever to return some sample documents
    mock_doc = Document(
        page_content="Sample T# documentation content",
        metadata={"source": "test.md"}
    )
    mock_retriever.get_relevant_documents.return_value = [mock_doc]
    
    return mock_store

def test_chain_creation(qa_manager, mock_vector_store):
    """Test QA chain creation"""
    chain = qa_manager.create_qa_chain(mock_vector_store)
    assert chain is not None
    assert hasattr(chain, '__call__')
    logger.info("QA chain created successfully")

def test_memory_initialization(qa_manager):
    """Test memory initialization"""
    assert hasattr(qa_manager, 'memory')
    assert len(qa_manager.memory.chat_memory.messages) == 0
    logger.info("Memory initialized correctly")

def test_chat_history_format(qa_manager):
    """Test chat history formatting"""
    # Add test messages
    qa_manager.memory.chat_memory.add_user_message("Test question")
    qa_manager.memory.chat_memory.add_ai_message("Test answer")
    
    # Get chat history
    history = qa_manager.get_chat_history()
    
    # Verify format
    assert len(history) == 2
    assert isinstance(history[0], HumanMessage)
    assert isinstance(history[1], AIMessage)
    logger.info("Chat history format verified")

def test_process_query(qa_manager, mock_vector_store):
    """Test query processing"""
    chain = qa_manager.create_qa_chain(mock_vector_store)
    
    # Mock the chain's __call__ method
    chain.__call__ = MagicMock(return_value={
        "answer": "Test answer",
        "source_documents": [Document(page_content="Test content", metadata={"source": "test.md"})]
    })
    
    result = qa_manager.process_query(chain, "How do I use variables in T#?")
    
    # Verify result structure
    assert 'answer' in result
    assert 'source_documents' in result
    assert 'chat_history' in result
    
    # Verify answer matches mock
    assert result['answer'] == "Test answer"
    
    # Verify memory was updated
    history = qa_manager.get_chat_history()
    assert len(history) == 2  # Question and answer
    assert isinstance(history[0], HumanMessage)
    assert isinstance(history[1], AIMessage)

def test_error_handling(qa_manager, mock_vector_store):
    """Test error handling in query processing"""
    chain = qa_manager.create_qa_chain(mock_vector_store)
    
    # Test with empty query
    result = qa_manager.process_query(chain, "")
    assert result['answer'] == "Please provide a valid question."
    
    # Test with chain error
    with patch('langchain.chains.ConversationalRetrievalChain.__call__', side_effect=ValueError("Test error")):
        result = qa_manager.process_query(chain, "test")
        assert "error occurred" in result['answer'].lower()
        assert "test error" in result['answer'].lower()
    logger.info("Error handling test completed")

def test_memory_persistence(qa_manager, mock_vector_store):
    """Test chat memory persistence across queries"""
    with patch('langchain.chains.ConversationalRetrievalChain.__call__') as mock_call:
        # Setup mock response
        mock_call.return_value = {
            "answer": "Test answer",
            "source_documents": [Document(page_content="Test content", metadata={"source": "test.md"})]
        }
        
        chain = qa_manager.create_qa_chain(mock_vector_store)
        
        # Process multiple queries
        queries = [
            "What is T#?",
            "How do I declare variables?",
            "Can you show an example?"
        ]
        
        for query in queries:
            result = qa_manager.process_query(chain, query)
            assert result['answer'] == "Test answer"
        
        # Verify memory contains all interactions
        history = qa_manager.get_chat_history()
        assert len(history) == len(queries) * 2  # Each query should have a response
        assert all(isinstance(msg, (HumanMessage, AIMessage)) for msg in history)
        logger.info("Memory persistence test completed")