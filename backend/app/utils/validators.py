# app/utils/validators.py
import logging
from typing import List, Dict, Any
from langchain.schema import Document
import numpy as np
import cohere  # Import the whole module instead

logger = logging.getLogger(__name__)

class DocumentValidator:
    def __init__(self):
        self.required_metadata_fields = {'source', 'type'}
        self.max_content_length = 8192  # Maximum content length
        
    def validate_document(self, doc: Document) -> bool:
        """Validate a single document"""
        try:
            # Check document structure
            if not isinstance(doc, Document):
                raise ValueError(f"Invalid document type: {type(doc)}")
                
            # Validate content
            if not doc.page_content or not isinstance(doc.page_content, str):
                raise ValueError("Invalid or empty page content")
                
            if len(doc.page_content) > self.max_content_length:
                raise ValueError(f"Content length exceeds maximum: {len(doc.page_content)} > {self.max_content_length}")
                
            # Validate metadata
            if not doc.metadata:
                raise ValueError("Missing metadata")
                
            missing_fields = self.required_metadata_fields - set(doc.metadata.keys())
            if missing_fields:
                raise ValueError(f"Missing required metadata fields: {missing_fields}")
                
            return True
            
        except Exception as e:
            logger.error(f"Document validation failed: {str(e)}")
            return False
            
    def validate_documents(self, documents: List[Document]) -> List[Document]:
        """Validate a list of documents and return only valid ones"""
        valid_docs = []
        for doc in documents:
            if self.validate_document(doc):
                valid_docs.append(doc)
            else:
                logger.warning(f"Skipping invalid document: {doc.metadata.get('source', 'unknown')}")
                
        logger.info(f"Validated {len(valid_docs)}/{len(documents)} documents")
        return valid_docs

class EmbeddingValidator:
    def __init__(self, expected_dim: int = 768):  # Default Cohere embedding dimension
        self.expected_dim = expected_dim
        
    def validate_embeddings(self, embeddings: np.ndarray) -> bool:
        """Validate embedding dimensions and values"""
        try:
            if embeddings.shape[1] != self.expected_dim:
                raise ValueError(f"Invalid embedding dimension: {embeddings.shape[1]} != {self.expected_dim}")
                
            # Check for NaN or infinite values
            if np.any(np.isnan(embeddings)) or np.any(np.isinf(embeddings)):
                raise ValueError("Embeddings contain NaN or infinite values")
                
            # Check for zero vectors
            zero_vectors = np.all(embeddings == 0, axis=1)
            if np.any(zero_vectors):
                raise ValueError("Embeddings contain zero vectors")
                
            return True
            
        except Exception as e:
            logger.error(f"Embedding validation failed: {str(e)}")
            return False

def handle_cohere_error(e: Exception) -> None:
    """Handle Cohere API errors"""
    error_map = {
        'invalid_api_key': "Invalid Cohere API key. Please check your configuration.",
        'rate_limit': "Rate limit exceeded. Please retry after some time.",
        'invalid_model': "Invalid model specified for embeddings.",
        'context_length': "Document length exceeds model's context window."
    }
    
    error_type = str(e)
    for key in error_map:
        if key in error_type.lower():
            error_message = error_map[key]
            break
    else:
        error_message = f"Cohere API error: {str(e)}"
    
    logger.error(error_message)
    raise ValueError(error_message)