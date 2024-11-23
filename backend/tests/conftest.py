import os
import sys
import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import MagicMock
from typing import Dict, Any, Generator, List
import logging
import uuid
from datetime import datetime
import logging.handlers
import atexit
import threading

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_anthropic import ChatAnthropic
from langchain_cohere import CohereEmbeddings
from dotenv import load_dotenv

# Create a lock for thread-safe logging
logging_lock = threading.Lock()

class ThreadSafeHandler(logging.StreamHandler):
    """Thread-safe logging handler"""
    def emit(self, record):
        with logging_lock:
            try:
                super().emit(record)
            except Exception:
                self.handleError(record)

def setup_logging():
    """Configure logging with thread safety and proper cleanup"""
    root = logging.getLogger()
    
    # Remove existing handlers
    for handler in root.handlers[:]:
        handler.close()
        root.removeHandler(handler)
        
    # Add thread-safe stream handler
    handler = ThreadSafeHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    
    def cleanup():
        """Clean up logging handlers"""
        handlers = root.handlers[:]
        for handler in handlers:
            try:
                handler.flush()
                handler.close()
            except Exception:
                pass
            try:
                root.removeHandler(handler)
            except Exception:
                pass
    
    # Register cleanup
    atexit.register(cleanup)
    return root

# Load environment variables from .env
load_dotenv()

class TestConfig:
    """Test configuration management with production-like settings"""
    
    # API Keys from environment
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    COHERE_API_KEY = os.getenv('COHERE_API_KEY')
    
    # Test environment settings
    TEST_ENV = {
        'ALLOWED_ORIGIN': 'http://localhost:3000',
        'VECTOR_STORE_TOP_K': '3',
        'CHUNK_SIZE': '1000',
        'CHUNK_OVERLAP': '200',
        'ENABLE_CACHE': 'false',
        'TEST_MODE': 'true',
        'MIN_CHUNK_SIZE': '100',
        'MAX_CHUNK_SIZE': '3000',
        'CODE_CHUNK_SIZE': '2000',
        'CODE_CHUNK_OVERLAP': '200',
        'FLASK_ENV': 'testing',
        'FLASK_DEBUG': 'true',
        'MAX_RETRIES': '3',
        'RETRY_DELAY': '1.0',
        'LLM_TEMPERATURE': '0.3',
        'LLM_MAX_TOKENS': '4096',
        'MMR_DIVERSITY_SCORE': '0.3'
    }
    
    # Production-like test documents
    TEST_DOCUMENTS = [
        {
            'content': """# T# Variables
            ## Type
            ruleset
            ## Content
            Variables in T# are declared using the var keyword.
            ```csharp
            var x = 10;
            var name = "Player";
            ```
            """,
            'metadata': {'source': 'variables.md', 'type': 'ruleset'}
        },
        {
            'content': """# T# Functions
            ## Type
            functions
            ## Content
            Functions are declared using the func keyword.
            ```csharp
            func Add(a: int, b: int) -> int {
                return a + b;
            }
            ```
            """,
            'metadata': {'source': 'functions.md', 'type': 'functions'}
        },
        {
            'content': """# Game Objects
            ## Type
            example
            ## Content
            Here's how to work with game objects:
            ```csharp
            var player = GameObject.Find("Player");
            player.transform.position = new Vector3(0, 0, 0);
            ```
            """,
            'metadata': {'source': 'gameobjects.md', 'type': 'example'}
        },
        {
            'content': """# Error Handling
            ## Type
            ruleset
            ## Content
            Error handling in T# follows these patterns:
            ```csharp
            try {
                riskyOperation();
            } catch (Exception e) {
                LogError(e.Message);
            }
            ```
            """,
            'metadata': {'source': 'error_handling.md', 'type': 'ruleset'}
        },
        {
            'content': """# Performance Best Practices
            ## Type
            example
            ## Content
            Optimize your T# code with these patterns:
            ```csharp
            // Cache component references
            private Transform _transform;
            void Start() {
                _transform = GetComponent<Transform>();
            }
            ```
            """,
            'metadata': {'source': 'performance.md', 'type': 'example'}
        }
    ]
    
    @classmethod
    def validate_config(cls) -> None:
        """Validate test configuration"""
        missing_env = []
        if not cls.ANTHROPIC_API_KEY:
            missing_env.append("ANTHROPIC_API_KEY")
        if not cls.COHERE_API_KEY:
            missing_env.append("COHERE_API_KEY")
            
        if missing_env:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_env)}")
            
        # Validate test environment settings
        for key, value in cls.TEST_ENV.items():
            if value is None:
                raise ValueError(f"Missing test environment setting: {key}")

def get_test_id():
    """Generate unique test run identifier"""
    return f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

@pytest.fixture(scope="session")
def test_id():
    """Provide unique test run identifier that's used across the test session"""
    return get_test_id()

@pytest.fixture(scope="session")
def logger():
    """Provide a session-wide logger"""
    return setup_logging()

@pytest.fixture(scope="session", autouse=True)
def test_env(test_id, logger) -> Generator[Dict[str, str], None, None]:
    """Setup and teardown test environment with cleanup"""
    TestConfig.validate_config()
    
    original_env = dict(os.environ)
    temp_dirs = []
    
    try:
        # Setup test environment
        env_vars = {
            'ANTHROPIC_API_KEY': TestConfig.ANTHROPIC_API_KEY,
            'COHERE_API_KEY': TestConfig.COHERE_API_KEY,
            'TEST_RUN_ID': test_id,
            **TestConfig.TEST_ENV
        }
        os.environ.update(env_vars)
        
        # Create temporary test directories
        temp_dir = Path(tempfile.mkdtemp(prefix=f"test_{test_id}_"))
        temp_dirs.append(temp_dir)
        
        test_kb_path = temp_dir / "knowledge_base"
        test_kb_path.mkdir(parents=True)
        
        # Set knowledge base path in environment
        os.environ['KNOWLEDGE_BASE_PATH'] = str(test_kb_path)
        
        # Create test knowledge base files
        for doc in TestConfig.TEST_DOCUMENTS:
            file_path = test_kb_path / doc['metadata']['source']
            file_path.write_text(doc['content'])
        
        yield env_vars
        
    finally:
        # Cleanup
        for temp_dir in temp_dirs:
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                    logger.info(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"Error cleaning up {temp_dir}: {e}")
        
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)
        logger.info("Test environment cleanup completed")

@pytest.fixture(scope="session")
def test_documents(test_env) -> List[Document]:
    """Provide test documents with proper cleanup"""
    docs = [
        Document(
            page_content=doc['content'],
            metadata={
                **doc['metadata'],
                'test_id': test_env['TEST_RUN_ID']
            }
        ) for doc in TestConfig.TEST_DOCUMENTS
    ]
    
    yield docs
    
    # Cleanup any test-specific data
    logger.info(f"Cleaning up test documents for run {test_env['TEST_RUN_ID']}")

@pytest.fixture(scope="session")
def test_knowledge_base(test_env) -> Path:
    """Provide path to test knowledge base"""
    return Path(os.environ['KNOWLEDGE_BASE_PATH'])

@pytest.fixture(scope="function")
def mock_llm():
    """Provide a mock LLM for testing"""
    mock = MagicMock()
    mock.invoke.return_value = "Test response"
    return mock

@pytest.fixture(scope="function")
def mock_embeddings():
    """Provide mock embeddings for testing"""
    mock = MagicMock()
    mock.embed_documents.return_value = [[0.1] * 768]
    mock.embed_query.return_value = [0.1] * 768
    return mock

@pytest.fixture(scope="function")
def mock_vector_store(mock_embeddings):
    """Provide mock vector store for testing"""
    mock = MagicMock()
    mock.similarity_search.return_value = []
    return mock

@pytest.fixture(scope="function")
def cleanup_vector_store():
    """Fixture to handle vector store cleanup"""
    yield
    # Cleanup is handled by the logger fixture

@pytest.fixture(scope="function")
def app(test_env, logger):
    """Create test Flask application with proper cleanup"""
    from app.main import create_app
    
    app = create_app(force_recreate=True)
    app.config.update({
        'TESTING': True,
        'TEST_RUN_ID': test_env['TEST_RUN_ID']
    })
    
    yield app
    
    # Cleanup
    if hasattr(app, 'vector_store'):
        try:
            app.vector_store.cleanup_all()
        except Exception as e:
            logger.warning(f"Error during vector store cleanup: {e}")

@pytest.fixture(scope="function")
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture(scope="function")
def app_context(app):
    """Provide application context"""
    with app.app_context() as ctx:
        yield ctx

def pytest_configure(config):
    """Configure pytest with custom markers and logging"""
    import warnings
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    setup_logging()
    
    # Filter known warnings
    warnings.filterwarnings(
        "ignore", 
        category=DeprecationWarning,
        module="pydantic.*"
    )
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        module="google.*"
    )
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        message="pkg_resources is deprecated.*"
    )
    
    # Filter LangChain warnings
    warnings.filterwarnings(
        "ignore",
        category=Warning,
        message=".*ConversationBufferMemory.*"
    )
    warnings.filterwarnings(
        "ignore",
        message=".*get_relevant_documents.*"
    )
    
    # Add markers
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "e2e: mark test as end-to-end test")
    config.addinivalue_line("markers", "performance: mark test as performance test")
    config.addinivalue_line("markers", "deployment: mark test as deployment readiness test")

def pytest_collection_modifyitems(config, items):
    """Modify test items to add markers based on location"""
    for item in items:
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
            
    # Add deployment marker to deployment-related tests
    deployment_keywords = ['deploy', 'render', 'production', 'gunicorn']
    for item in items:
        if any(keyword in item.name.lower() for keyword in deployment_keywords):
            item.add_marker(pytest.mark.deployment)

@pytest.fixture(scope="session")
def performance_threshold():
    """Provide performance test thresholds"""
    return {
        'api_response_time': 2.0,  # seconds
        'vector_search_time': 1.0,  # seconds
        'memory_usage': 500 * 1024 * 1024,  # 500MB
    }

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add custom summary information to test report"""
    if hasattr(terminalreporter, 'stats'):
        terminalreporter.write_sep("=", "Test Summary")
        
        # Collect test results by type
        results = {
            'unit': {'passed': 0, 'failed': 0},
            'integration': {'passed': 0, 'failed': 0},
            'e2e': {'passed': 0, 'failed': 0},
            'deployment': {'passed': 0, 'failed': 0}
        }
        
        for report in terminalreporter.getreports(''):
            for marker in ['unit', 'integration', 'e2e', 'deployment']:
                if f'tests/{marker}/' in str(report.nodeid):
                    if report.passed:
                        results[marker]['passed'] += 1
                    elif report.failed:
                        results[marker]['failed'] += 1
        
        # Print results
        for test_type, counts in results.items():
            total = counts['passed'] + counts['failed']
            if total > 0:
                pass_rate = (counts['passed'] / total) * 100
                terminalreporter.write_line(
                    f"{test_type.capitalize()} Tests: "
                    f"{counts['passed']} passed, {counts['failed']} failed "
                    f"({pass_rate:.1f}% pass rate)"
                )
        
        # Cleanup logging handlers
        root_logger = logging.getLogger()
        handlers = root_logger.handlers[:]
        for handler in handlers:
            try:
                handler.flush()
                handler.close()
            except Exception:
                pass
            try:
                root_logger.removeHandler(handler)
            except Exception:
                pass

def pytest_sessionfinish(session):
    """Clean up after all tests are done"""
    # Get root logger
    root_logger = logging.getLogger()
    
    # Clean up handlers
    handlers = root_logger.handlers[:]
    for handler in handlers:
        try:
            handler.flush()
            handler.close()
        except Exception:
            pass
        try:
            root_logger.removeHandler(handler)
        except Exception:
            pass
    
    # Final shutdown
    logging.shutdown()