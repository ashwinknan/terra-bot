import pytest
import os
from pathlib import Path
import tempfile
import shutil
from unittest.mock import MagicMock
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

@pytest.fixture(scope="session")
def test_env():
    """Setup test environment variables"""
    original_env = {
        key: os.environ.get(key)
        for key in [
            'ANTHROPIC_API_KEY',
            'COHERE_API_KEY',
            'ALLOWED_ORIGIN',
            'VECTOR_STORE_TOP_K',
            'CHUNK_SIZE',
            'ENABLE_CACHE'
        ]
    }
    
    os.environ.update({
        'ANTHROPIC_API_KEY': 'test-key',
        'COHERE_API_KEY': 'test-key',
        'ALLOWED_ORIGIN': 'http://localhost:3000',
        'VECTOR_STORE_TOP_K': '3',
        'CHUNK_SIZE': '1000',
        'ENABLE_CACHE': 'false'
    })
    
    yield
    
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

@pytest.fixture
def mock_documents():
    """Create mock documents for testing"""
    return [
        Document(
            page_content="Test document about variables in T#\nvar x = 10;\nvar y = 'test';",
            metadata={"source": "test.md", "type": "example"}
        ),
        Document(
            page_content="Function declaration in T#\nfunc testFunc() { }",
            metadata={"source": "test2.md", "type": "example"}
        )
    ]

@pytest.fixture
def mock_embeddings():
    """Mock embeddings function"""
    mock = MagicMock()
    mock.embed_query.return_value = [0.1] * 768
    mock.embed_documents.return_value = [[0.1] * 768]
    return mock

@pytest.fixture
def mock_vector_store(mock_documents, mock_embeddings):
    """Create mock vector store"""
    store = MagicMock(spec=Chroma)
    store._collection.count.return_value = len(mock_documents)
    return store
