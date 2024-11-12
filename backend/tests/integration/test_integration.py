import unittest
import logging
import sys
import time
import tempfile
import shutil
from pathlib import Path
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from app.core.document_processor import DocumentProcessor
from app.core.vector_store import VectorStoreManager
from app.core.qa_chain import QAChainManager
from app.core.initializer import initialize_app, AppComponents


class BaseTestCase(unittest.TestCase):
    """Base test case with common setup and teardown"""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources"""
        VectorStoreManager.reset_instances()
        
    def setUp(self):
        """Set up test environment"""
        VectorStoreManager.reset_instances()
        
    def tearDown(self):
        """Clean up test environment"""
        try:
            if hasattr(self, 'temp_dir'):
                shutil.rmtree(self.temp_dir)
            VectorStoreManager.reset_instances()
        except Exception as e:
            logger.error(f"Error during teardown: {str(e)}")


class TestDocumentProcessorIntegration(BaseTestCase):
    """Test DocumentProcessor integration with other components"""
    
    def setUp(self):
        """Set up test environment"""
        super().setUp()
        self.temp_dir = Path(tempfile.mkdtemp())
        self.knowledge_base_path = self.temp_dir / "knowledge_base"
        self.summaries_path = self.temp_dir / "summaries"
        self.knowledge_base_path.mkdir()
        self.summaries_path.mkdir()

        # Create a variety of test markdown files
        self.test_files = [
            ("basic.md", "# Basic Document\nThis is a basic test document."),
            ("complex.md", """# Complex Document
## Section 1
This is a more complex document with multiple sections.
## Section 2
It includes code samples:
```tsharp
var x = 10;
var y = "test";
```
            """),
            ("empty.md", ""),  # Edge case: empty file
            ("special_chars.md", """# Special Characters Test
This document has special characters: !@#$%^&*()
And some código UTF-8 characters too."""),
            ("long.md", "# " + "Very Long Document\n" + "Test content\n" * 100)  # Long document
        ]
        
        # Create all test files
        for filename, content in self.test_files:
            file_path = self.knowledge_base_path / filename
            file_path.write_text(content)
        
        # Initialize document processor
        self.doc_processor = DocumentProcessor(
            str(self.knowledge_base_path),
            str(self.summaries_path)
        )

    def test_document_loading(self):
        """Test document loading capabilities"""
        documents = self.doc_processor.load_documents()
        self.assertTrue(len(documents) > 0, "No documents loaded")
        self.assertEqual(len(documents), len(self.test_files), 
                        f"Expected {len(self.test_files)} documents, got {len(documents)}")

        # Verify document contents
        doc_contents = [doc.page_content for doc in documents]
        self.assertTrue(any("Basic Document" in content for content in doc_contents), 
                      "Basic document not found")
        self.assertTrue(any("código UTF-8" in content for content in doc_contents), 
                      "UTF-8 characters not preserved")

    def test_summary_generation(self):
        """Test summary generation capabilities"""
        summaries = self.doc_processor.generate_summaries()
        self.assertTrue(len(summaries) > 0, "No summaries generated")
        
        # Check if summaries were saved
        summary_file = self.summaries_path / "summaries.json"
        self.assertTrue(summary_file.exists(), "Summary file not created")
        
        # Verify summary contents
        self.assertTrue(any("basic" in key.lower() for key in summaries.keys()),
                      "Basic document summary not found")

    def test_vector_store_creation(self):
        """Test vector store creation and querying"""
        try:
            # Load documents and create summaries
            documents = self.doc_processor.load_documents()
            summaries = self.doc_processor.generate_summaries()
            
            # Create vector store
            vector_store_manager = VectorStoreManager(self.doc_processor)
            vector_store = vector_store_manager.get_or_create_vector_store(
                force_recreate=True,
                summaries=summaries
            )
            
            # Verify vector store creation
            self.assertIsNotNone(vector_store, "Vector store creation failed")
            self.assertTrue(hasattr(vector_store, '_collection'), "No collection in vector store")
            
            # Verify document count
            collection = vector_store._collection
            doc_count = collection.count()
            self.assertEqual(doc_count, len(documents), 
                           f"Expected {len(documents)} documents in vector store, got {doc_count}")
            
            # Try a simple similarity search
            results = vector_store.similarity_search("basic document", k=1)
            self.assertTrue(len(results) > 0, "No search results returned")
            self.assertTrue(isinstance(results[0].page_content, str), 
                          "Invalid search result format")
            
        except Exception as e:
            self.fail(f"Vector store creation failed with error: {str(e)}")


class TestFullSystemIntegration(BaseTestCase):
    """Test complete system integration"""
    
    def setUp(self):
        """Set up test environment"""
        super().setUp()
        self.temp_dir = Path(tempfile.mkdtemp())
        self.knowledge_base_path = self.temp_dir / "knowledge_base"
        self.summaries_path = self.temp_dir / "summaries"
        self.knowledge_base_path.mkdir()
        self.summaries_path.mkdir()
        
        # Create test documentation
        self.test_content = """
# T# Programming Guide

## Variables
Variables in T# are similar to C# but with some key differences.
### Declaration
Use 'var' keyword for local variables:
```tsharp
var health = 100;
var name = "Player";
```

## Functions
Functions are declared using the 'func' keyword:
```tsharp
func Calculate(x: int, y: int) -> int {
    return x + y;
}
```

## Game Objects
Access game objects using the following syntax:
```tsharp
var player = GameObject.Find("Player");
var position = player.transform.position;
```
        """
        
        # Create the test file
        test_md = self.knowledge_base_path / "tsharp_guide.md"
        test_md.write_text(self.test_content)

    def test_system_initialization(self):
        """Test system initialization"""
        try:
            initialize_app(force_recreate=True)
            
            # Verify components
            self.assertIsNotNone(AppComponents.doc_processor, "Document processor not initialized")
            self.assertIsNotNone(AppComponents.vector_store, "Vector store not initialized")
            self.assertIsNotNone(AppComponents.qa_chain, "QA chain not initialized")
            
            # Verify document loading
            collection = AppComponents.vector_store._collection
            self.assertTrue(collection.count() > 0, "No documents in vector store")
        except Exception as e:
            self.fail(f"System initialization failed with error: {str(e)}")

    def test_query_processing(self):
        """Test query processing capabilities"""
        try:
            initialize_app(force_recreate=True)
            
            # Test various query types
            queries = [
                ("How do I declare variables in T#?", "var keyword"),
                ("What is the syntax for functions?", "func keyword"),
                ("How do I access game objects?", "GameObject.Find"),
            ]
            
            for query, expected_content in queries:
                result = AppComponents.qa_chain({"question": query})
                
                # Verify response structure
                self.assertIn('answer', result, f"No answer for query: {query}")
                self.assertIn('source_documents', result, f"No sources for query: {query}")
                
                # Verify answer content
                answer = result['answer']
                self.assertIsInstance(answer, str, "Answer should be string")
                self.assertGreater(len(answer), 0, "Answer shouldn't be empty")
                
                # Verify source documents
                sources = result['source_documents']
                self.assertTrue(len(sources) > 0, "No source documents returned")
                
                # Verify relevant content is found
                found_relevant_content = any(
                    expected_content.lower() in doc.page_content.lower() 
                    for doc in sources
                )
                self.assertTrue(found_relevant_content, 
                              f"Expected content '{expected_content}' not found in sources")
        except Exception as e:
            self.fail(f"Query processing failed with error: {str(e)}")

    def test_error_handling(self):
        """Test system error handling"""
        try:
            initialize_app(force_recreate=True)
            
            # Test empty query
            result = AppComponents.qa_chain({"question": ""})
            self.assertIn('answer', result, "No response for empty query")
            
            # Test very long query
            long_query = "how to " * 100
            result = AppComponents.qa_chain({"question": long_query})
            self.assertIn('answer', result, "No response for long query")
            
            # Test special characters
            special_query = "How do I use !@#$%^&*() in T#?"
            result = AppComponents.qa_chain({"question": special_query})
            self.assertIn('answer', result, "No response for query with special characters")
        except Exception as e:
            self.fail(f"Error handling test failed with error: {str(e)}")


def run_integration_tests():
    """Run all integration tests and return results"""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestDocumentProcessorIntegration,
        TestFullSystemIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


if __name__ == '__main__':
    # Suppress warnings during test execution
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = run_integration_tests()
        
    # Print summary
    print("\nIntegration Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    # Exit with appropriate code
    sys.exit(not result.wasSuccessful())