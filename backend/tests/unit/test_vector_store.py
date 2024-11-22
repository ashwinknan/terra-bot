import pytest
from app.core.vector_store import VectorStoreManager

def test_vector_store_initialization(mock_documents):
    manager = VectorStoreManager()
    assert manager.embeddings is not None
    assert manager.chroma_client is not None

def test_vector_store_creation(mock_documents, mock_embeddings):
    manager = VectorStoreManager()
    vector_store = manager.create_vector_store(mock_documents)
    assert vector_store is not None
    assert vector_store._collection.count() > 0

def test_similarity_search(mock_documents, mock_embeddings):
    manager = VectorStoreManager()
    vector_store = manager.create_vector_store(mock_documents)
    
    results = manager.similarity_search_with_filter(
        "test query",
        {"doc_type": "example"},
        k=2
    )
    assert len(results) <= 2