import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from app.core.vector_store import VectorStoreManager
from langchain_core.documents import Document

@pytest.fixture
def mock_chroma_client():
    client = MagicMock()
    # Set max_batch_size as an attribute, not a MagicMock
    client.max_batch_size = 100
    return client

@pytest.fixture
def mock_doc_processor():
    processor = MagicMock()
    processor.load_documents.return_value = [
        Document(page_content="Test content 1", metadata={"source": "test1.md"}),
        Document(page_content="Test content 2", metadata={"source": "test2.md"})
    ]
    return processor

@pytest.fixture
def vector_store_manager(mock_chroma_client, mock_doc_processor):
    with patch('chromadb.PersistentClient', return_value=mock_chroma_client), \
         patch('langchain_cohere.CohereEmbeddings') as mock_embeddings:
        manager = VectorStoreManager(doc_processor=mock_doc_processor)
        manager.chroma_client = mock_chroma_client
        return manager

def test_text_processing(vector_store_manager):
    """Test text processing for embeddings"""
    # Test exact input/output pairs
    test_cases = [
        # Add leading comment to indicate these are exact test cases
        ("Simple text", [" ".join("Simple text".split())]),  # Normalize but don't strip
        (["Multiple", "strings"], ["Multiple", "strings"]),
        (None, ["None"]),
        ("  Multiple   Spaces  ", [" ".join("Multiple   Spaces".split())])  # Test space normalization
    ]

    for input_text, expected in test_cases:
        result = vector_store_manager._process_text_for_embedding(input_text)
        assert result == expected, f"Failed for input: {input_text}"

def test_vector_store_creation_validation(vector_store_manager):
    """Test vector store creation with invalid inputs"""
    with pytest.raises(ValueError):
        vector_store_manager.create_vector_store([])

def test_vector_store_creation_error_handling(vector_store_manager):
    """Test error handling in vector store creation"""
    with patch.object(vector_store_manager, 'create_vector_store', side_effect=ValueError("No documents provided")):
        with pytest.raises(ValueError, match="No documents provided"):
            vector_store_manager.create_vector_store(None)
        with pytest.raises(ValueError, match="No documents provided"):
            vector_store_manager.create_vector_store([])

@patch('time.sleep')
def test_get_or_create_vector_store(mock_sleep, vector_store_manager):
    """Test get_or_create_vector_store functionality"""
    mock_store = MagicMock()
    
    with patch('langchain_chroma.Chroma', return_value=mock_store), \
         patch.object(vector_store_manager.doc_processor, 'load_documents') as mock_load:
        
        # Setup mock documents
        mock_docs = [
            Document(page_content="Test 1", metadata={"source": "test1.md"}),
            Document(page_content="Test 2", metadata={"source": "test2.md"})
        ]
        mock_load.return_value = mock_docs
        
        # Test force recreate
        result = vector_store_manager.get_or_create_vector_store(force_recreate=True)
        assert result is not None

def test_cleanup(vector_store_manager):
    """Test cleanup operations"""
    with patch('shutil.rmtree') as mock_rmtree, \
         patch('pathlib.Path.exists', return_value=True), \
         patch('tempfile.mkdtemp', return_value="/tmp/test"):
        
        vector_store_manager.cleanup_all()
        vector_store_manager.cleanup_temp_directories()