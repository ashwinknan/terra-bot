# tests/unit/test_components.py

import unittest
import logging
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import warnings
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from app.utils.text_splitter import CustomMarkdownSplitter
from app.utils.validators import DocumentValidator, EmbeddingValidator, handle_cohere_error
from langchain_core.documents import Document

class TestEnvironment(unittest.TestCase):
    """Test environment and dependencies"""
    
    def test_dependencies(self):
        """Test if required packages are installed"""
        required_packages = [
            'langchain',
            'langchain_anthropic',
            'langchain_core',
            'langchain_community',
            'chromadb',
            'cohere'
        ]
        for package in required_packages:
            try:
                __import__(package)
            except ImportError as e:
                self.fail(f"Required package {package} not installed: {str(e)}")

class TestTextSplitter(unittest.TestCase):
    """Test CustomMarkdownSplitter functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.splitter = CustomMarkdownSplitter(chunk_size=100, chunk_overlap=20)

    def test_text_splitting(self):
        """Test text splitting"""
        test_text = "# Header\nThis is a test.\n## Subheader\nMore test content."
        chunks = self.splitter.split_text(test_text)
        self.assertTrue(len(chunks) > 0, "Text splitting failed")
        self.assertTrue(all(len(chunk) <= 100 for chunk in chunks))
        
    def test_empty_text(self):
        """Test splitting empty text"""
        chunks = self.splitter.split_text("")
        self.assertEqual(len(chunks), 0, "Empty text should produce no chunks")
        
    def test_header_splitting(self):
        """Test that headers trigger new chunks"""
        test_text = "Content 1\n# Header\nContent 2"
        chunks = self.splitter.split_text(test_text)
        self.assertEqual(len(chunks), 2, "Header should trigger new chunk")

class TestValidators(unittest.TestCase):
    """Test validator functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.doc_validator = DocumentValidator()
        self.embedding_validator = EmbeddingValidator()

    def test_valid_document(self):
        """Test validation of valid document"""
        valid_doc = Document(
            page_content="Test content",
            metadata={"source": "test.md", "type": "markdown"}
        )
        self.assertTrue(self.doc_validator.validate_document(valid_doc))
        
    def test_invalid_document(self):
        """Test validation of invalid document"""
        invalid_doc = Document(
            page_content="",  # Empty content
            metadata={"source": "test.md"}  # Missing type
        )
        self.assertFalse(self.doc_validator.validate_document(invalid_doc))
        
    def test_document_length(self):
        """Test document length validation"""
        long_doc = Document(
            page_content="x" * 10000,  # Exceeds max length
            metadata={"source": "test.md", "type": "markdown"}
        )
        self.assertFalse(self.doc_validator.validate_document(long_doc))
        
    def test_embedding_validation(self):
        """Test embedding validation"""
        # Create valid embeddings
        valid_embeddings = np.random.rand(10, 768)  # 768 is default dimension
        self.assertTrue(self.embedding_validator.validate_embeddings(valid_embeddings))
        
        # Test invalid dimension
        invalid_embeddings = np.random.rand(10, 100)  # Wrong dimension
        self.assertFalse(self.embedding_validator.validate_embeddings(invalid_embeddings))
        
        # Test NaN values
        nan_embeddings = np.full((10, 768), np.nan)
        self.assertFalse(self.embedding_validator.validate_embeddings(nan_embeddings))

    def test_cohere_error_handling(self):
        """Test Cohere error handling"""
        with self.assertRaises(ValueError):
            handle_cohere_error(Exception("invalid_api_key: Invalid API key"))
        
        with self.assertRaises(ValueError):
            handle_cohere_error(Exception("rate_limit: Too many requests"))

def run_unit_tests():
    """Run all unit tests and return results"""
    suite = unittest.TestSuite()
    test_classes = [
        TestEnvironment,
        TestTextSplitter,
        TestValidators
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)

if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = run_unit_tests()
        
    print("\nUnit Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    sys.exit(not result.wasSuccessful())