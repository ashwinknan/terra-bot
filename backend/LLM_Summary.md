# RAG Chatbot Implementation Documentation

This document describes the code for a RAG chatbot and how the files are organized. Below you'll find the complete source code and structure of the implementation.

## Complete Directory Structure
```
└── backend
    ├── .cache
    │   └── chroma.sqlite3
    ├── .pytest_cache
    │   ├── v
    │   │   └── cache
    │   │       ├── lastfailed
    │   │       ├── nodeids
    │   │       └── stepwise
    │   ├── .gitignore
    │   ├── CACHEDIR.TAG
    │   └── README.md
    ├── app
    │   ├── api
    │   │   └── routes.py
    │   ├── config
    │   │   ├── __init__.py
    │   │   ├── prompt_templates.py
    │   │   └── settings.py
    │   ├── core
    │   │   ├── __init__.py
    │   │   ├── document_processor.py
    │   │   ├── initializer.py
    │   │   ├── qa_chain.py
    │   │   └── vector_store.py
    │   ├── utils
    │   │   ├── __init__.py
    │   │   ├── llm_test.py
    │   │   ├── text_splitter.py
    │   │   ├── validators.py
    │   │   └── version_check.py
    │   ├── .DS_Store
    │   ├── __init__.py
    │   └── main.py
    ├── data
    │   ├── knowledge_base
    │   │   ├── .DS_Store
    │   │   ├── Mountrain Climber Controller_documentation.md
    │   │   ├── SpaceMarshal_documentation.md
    │   │   ├── T# Accessing Components & Game Objects.md
    │   │   ├── T# Adding Audio.md
    │   │   ├── T# Adding Haptics.md
    │   │   ├── T# Basics.md
    │   │   ├── T# Coroutines.md
    │   │   ├── T# Event Functions.md
    │   │   ├── T# Limitations.md
    │   │   ├── T# Loading Scenes.md
    │   │   ├── T# Particles.md
    │   │   ├── T# StudioAnalytics.md
    │   │   ├── T# StudioExtensions.md
    │   │   ├── T# StudioLeaderboard.md
    │   │   ├── T# StudioPrefs.md
    │   │   ├── T# StudioUser.md
    │   │   ├── T# Variables.md
    │   │   ├── T# Working with the Player.md
    │   │   ├── T# Wrappers.md
    │   │   ├── Traffic Rider Controller_documentation.md
    │   │   └── World War Controller_documentation.md
    │   └── .DS_Store
    ├── scripts
    │   ├── __init__.py
    │   ├── generate_summaries.py
    │   └── recreate_vector_store.py
    ├── tests
    │   ├── integration
    │   │   └── test_integration.py
    │   ├── unit
    │   │   ├── __init__.py
    │   │   ├── test_anthropic.py
    │   │   ├── test_components.py
    │   │   └── test_qa_chain.py
    │   └── __Init__.py
    ├── .DS_Store
    ├── .env
    ├── Codebase_Summary.md
    ├── requirements.txt
    ├── run.py
    ├── runtime.txt
    └── wsgi.py
```

## Scanned Folders:
- app
- data
- scripts
- tests

## Code Contents

# File: app/__init__.py
```python
from app.main import create_app
```

# File: app/main.py
```python
# app/main.py
import logging
import argparse
from flask import Flask
from flask_cors import CORS
from app.api.routes import api_bp
from app.core.initializer import initialize_app
from app.utils.version_check import check_versions
from app.utils.llm_test import test_llm
from app.config.settings import DEBUG, ALLOWED_ORIGIN

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app(force_recreate=False):
    """Application factory function"""
    # Check versions before starting
    if not check_versions():
        logger.warning("Version mismatches detected. Application may not work as expected.")

    # Test LLM
    if not test_llm():
        logger.error("LLM test failed - check your configuration")
        raise RuntimeError("LLM test failed")
    
    logger.info("Creating Flask application...")
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, origins=[ALLOWED_ORIGIN])
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Initialize components
    logger.info("Initializing application components...")
    initialize_app(force_recreate)
    
    logger.info("Application creation completed successfully")
    return app

def main():
    parser = argparse.ArgumentParser(description='Run the QA system')
    parser.add_argument('--recreate-vector-store', action='store_true', 
                      help='Force recreation of the vector store')
    args = parser.parse_args()

    app = create_app(force_recreate=args.recreate_vector_store)
    logger.info("Starting Flask server...")
    app.run(debug=DEBUG, host='0.0.0.0', port=5001)

if __name__ == '__main__':
    main()
```

# File: app/core/__init__.py
```python

```

# File: app/core/document_processor.py
```python
# app/core/document_processor.py

import logging
import re
import time
from pathlib import Path
from enum import Enum
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from langchain_core.documents import Document
from app.utils.text_splitter import CustomMarkdownSplitter
from app.config.settings import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

class ProcessingError(Exception):
    """Custom exception for document processing errors"""
    pass

class DocType(Enum):
    RULESET = "ruleset"
    LIMITATIONS = "limitations"
    FUNCTIONS = "functions"
    EXAMPLE = "example"
    
@dataclass
class DocumentMetadata:
    source: str
    doc_type: DocType
    title: str
    has_code: bool = False
    chunk_index: int = 0
    total_chunks: int = 1
    processing_attempts: int = 0

@dataclass
class ProcessingResult:
    success: bool
    documents: List[Document]
    errors: List[str]

class DocumentProcessor:
    def __init__(self, knowledge_base_path: str, 
                 max_retries: int = 3,
                 retry_delay: float = 1.0,
                 min_chunk_size: int = 100,
                 max_chunk_size: int = 3000):
        """Initialize document processor with configuration"""
        self.knowledge_base_path = Path(knowledge_base_path)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.processing_stats = {
            "total_files": 0,
            "successful_files": 0,
            "failed_files": 0,
            "total_chunks": 0,
            "retry_count": 0
        }
        self.custom_splitter = CustomMarkdownSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        logger.info(f"Initialized DocumentProcessor with path: {knowledge_base_path}")

    def _extract_document_type(self, content: str) -> DocType:
        """Extract document type from markdown content"""
        type_pattern = r'^## Type\s*\n([^\n]+)'
        if match := re.search(type_pattern, content, re.MULTILINE):
            doc_type = match.group(1).strip().lower()
            try:
                return DocType(doc_type)
            except ValueError:
                logger.warning(f"Unknown document type: {doc_type}, defaulting to FUNCTIONS")
                return DocType.FUNCTIONS
        return DocType.FUNCTIONS

    def _extract_title(self, content: str) -> str:
        """Extract document title from markdown content"""
        title_pattern = r'^# ([^\n]+)'
        if match := re.search(title_pattern, content):
            return match.group(1).strip()
        return "Untitled Document"

    def _process_document_by_type(self, content: str, file_name: str) -> List[Document]:
        """Process document based on its type"""
        try:
            # Extract document type and title
            doc_type = self._extract_document_type(content)
            title = self._extract_title(content)
            logger.info(f"Processing document {file_name} of type: {doc_type.value}")

            # Split content into chunks
            chunk_size = 1000 if doc_type in [DocType.RULESET, DocType.LIMITATIONS] else 2000
            chunk_overlap = 200 if doc_type in [DocType.RULESET, DocType.LIMITATIONS] else 100
            
            splitter = CustomMarkdownSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            
            chunks = splitter.split_text(content)
            logger.debug(f"Split document into {len(chunks)} chunks")

            # Create documents with metadata - Convert Enum to string
            documents = []
            for i, chunk in enumerate(chunks):
                if chunk.strip():  # Skip empty chunks
                    # Convert metadata to simple types
                    metadata = {
                        "source": file_name,
                        "doc_type": doc_type.value,  # Convert Enum to string
                        "title": title,
                        "has_code": bool(re.search(r'```', chunk)),
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "processing_attempts": 0
                    }
                    
                    doc = Document(
                        page_content=chunk,
                        metadata=metadata
                    )
                    documents.append(doc)

            logger.info(f"Successfully processed {len(documents)} chunks for {file_name}")
            return documents

        except Exception as e:
            logger.error(f"Error processing document {file_name}: {str(e)}")
            raise ProcessingError(f"Failed to process document: {str(e)}")

    def load_documents(self) -> List[Document]:
        """Load and process all documents with improved error handling"""
        all_documents = []
        failed_files = []
        self.processing_stats = {
            "total_files": 0,
            "successful_files": 0,
            "failed_files": 0,
            "total_chunks": 0,
            "retry_count": 0
        }
        
        logger.info(f"Starting document loading from {self.knowledge_base_path}")
        
        try:
            md_files = list(self.knowledge_base_path.glob('*.md'))
            self.processing_stats["total_files"] = len(md_files)
            
            for file_path in md_files:
                try:
                    logger.info(f"Processing file: {file_path.name}")
                    result = self._process_file_with_retry(file_path)
                    
                    if result.success and result.documents:
                        all_documents.extend(result.documents)
                        self.processing_stats["successful_files"] += 1
                        self.processing_stats["total_chunks"] += len(result.documents)
                        logger.info(f"Successfully processed {file_path.name}: {len(result.documents)} chunks created")
                    else:
                        failed_files.append((file_path.name, result.errors))
                        self.processing_stats["failed_files"] += 1
                        logger.warning(f"Failed to process {file_path.name} after all retries")
                        
                except Exception as e:
                    failed_files.append((file_path.name, [str(e)]))
                    self.processing_stats["failed_files"] += 1
                    logger.error(f"Error processing {file_path.name}: {str(e)}")
                    continue
            
            self._log_processing_summary(failed_files)
            
            if not all_documents:
                raise ValueError("No valid documents were successfully processed")
                
            return all_documents
            
        except Exception as e:
            logger.error(f"Critical error during document loading: {str(e)}")
            raise

    def _process_file_with_retry(self, file_path: Path) -> ProcessingResult:
        """Process a single file with retry logic"""
        errors = []
        retry_count = 0
        delay = self.retry_delay
        
        while retry_count <= self.max_retries:
            try:
                content = file_path.read_text(encoding='utf-8')
                documents = self._process_document_by_type(content, file_path.name)
                
                valid_documents = []
                for doc in documents:
                    try:
                        if self._validate_chunk(doc):
                            valid_documents.append(doc)
                    except ValueError as ve:
                        errors.append(f"Chunk validation error: {str(ve)}")
                        continue
                
                if valid_documents:
                    return ProcessingResult(True, valid_documents, errors)
                    
            except Exception as e:
                error_msg = f"Attempt {retry_count + 1}/{self.max_retries + 1} failed: {str(e)}"
                errors.append(error_msg)
                logger.warning(error_msg)
                
                if retry_count < self.max_retries:
                    logger.info(f"Retrying {file_path.name} in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2
                    retry_count += 1
                    self.processing_stats["retry_count"] += 1
                    continue
                    
                break
                
        return ProcessingResult(False, [], errors)

    def _validate_chunk(self, document: Document) -> bool:
        """Validate a document chunk"""
        content_length = len(document.page_content)
        
        if content_length < self.min_chunk_size:
            raise ValueError(f"Chunk too small ({content_length} chars)")
            
        if content_length > self.max_chunk_size:
            raise ValueError(f"Chunk too large ({content_length} chars)")
            
        if not document.page_content.strip():
            raise ValueError("Empty chunk")
            
        return True

    def _log_processing_summary(self, failed_files: List[Tuple[str, List[str]]]):
        """Log detailed processing summary"""
        logger.info("\n=== Document Processing Summary ===")
        logger.info(f"Total files processed: {self.processing_stats['total_files']}")
        logger.info(f"Successfully processed: {self.processing_stats['successful_files']}")
        logger.info(f"Failed to process: {self.processing_stats['failed_files']}")
        logger.info(f"Total chunks created: {self.processing_stats['total_chunks']}")
        logger.info(f"Total retry attempts: {self.processing_stats['retry_count']}")
        
        if failed_files:
            logger.warning("\nFailed Files Details:")
            for file_name, errors in failed_files:
                logger.warning(f"\n{file_name}:")
                for error in errors:
                    logger.warning(f"  - {error}")
                    
        logger.info("\n===============================")

    def get_processing_stats(self) -> Dict:
        """Get current processing statistics"""
        return self.processing_stats.copy()
```

# File: app/core/initializer.py
```python
# app/core/initializer.py

import logging
from pathlib import Path
import time
from typing import Any, Callable
from app.core.document_processor import DocumentProcessor
from app.core.vector_store import VectorStoreManager
from app.core.qa_chain import QAChainManager
from app.config.settings import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    MAX_RETRIES,  # Add this to settings.py with default value 3
    RETRY_DELAY,  # Add this to settings.py with default value 1.0
    MIN_CHUNK_SIZE,  # Add this to settings.py with default value 100
    MAX_CHUNK_SIZE   # Add this to settings.py with default value 3000
)

logger = logging.getLogger(__name__)

class AppComponents:
    """Singleton to store application components"""
    doc_processor = None
    vector_store_manager = None
    vector_store = None
    qa_chain_manager = None
    qa_chain = None

def _retry_with_backoff(func: Callable[[], Any], max_retries: int = 3, initial_delay: float = 1) -> Any:
    """
    Helper function to retry operations with exponential backoff
    """
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Final retry attempt failed: {str(e)}")
                raise
            delay = initial_delay * (2 ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay} seconds...")
            time.sleep(delay)

def initialize_app(force_recreate=False):
    """
    Initialize all application components with improved error handling and retries
    """
    try:
        logger.info("Starting application initialization...")
        
        # Setup paths
        base_path = Path(__file__).parent.parent.parent
        knowledge_base_path = base_path / "data" / "knowledge_base"
        
        # Ensure directory exists
        knowledge_base_path.mkdir(exist_ok=True, parents=True)
        
        # Initialize document processor with enhanced configuration
        logger.info("Initializing document processor...")
        AppComponents.doc_processor = DocumentProcessor(
            knowledge_base_path=str(knowledge_base_path),
            max_retries=MAX_RETRIES,
            retry_delay=RETRY_DELAY,
            min_chunk_size=MIN_CHUNK_SIZE,
            max_chunk_size=MAX_CHUNK_SIZE
        )
        
        # Load documents with enhanced error handling
        logger.info("Loading documents...")
        documents = AppComponents.doc_processor.load_documents()
        stats = AppComponents.doc_processor.get_processing_stats()
        logger.info(
            f"Document processing complete: "
            f"Processed {stats['total_files']} files, "
            f"Success: {stats['successful_files']}, "
            f"Failed: {stats['failed_files']}, "
            f"Total chunks: {stats['total_chunks']}, "
            f"Retries: {stats['retry_count']}"
        )
        
        # Initialize vector store manager
        logger.info("Initializing vector store manager...")
        AppComponents.vector_store_manager = VectorStoreManager(
            doc_processor=AppComponents.doc_processor
        )
        
        # Initialize vector store
        logger.info("Initializing vector store...")
        AppComponents.vector_store = _retry_with_backoff(
            lambda: AppComponents.vector_store_manager.get_or_create_vector_store(
                force_recreate=force_recreate
            )
        )

        # Initialize QA chain manager and create chain
        logger.info("Initializing QA chain...")
        AppComponents.qa_chain_manager = QAChainManager()
        AppComponents.qa_chain = AppComponents.qa_chain_manager.create_qa_chain(
            AppComponents.vector_store
        )
        
        logger.info("Application initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")
        raise RuntimeError(f"Failed to start server: {str(e)}")

def shutdown_app():
    """
    Safely shutdown all application components
    """
    logger.info("Shutting down application...")
    try:
        if AppComponents.vector_store_manager:
            AppComponents.vector_store_manager.cleanup_all()
        if AppComponents.qa_chain_manager:
            AppComponents.qa_chain_manager.clear_memory()
        logger.info("Application shutdown completed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
```

# File: app/core/qa_chain.py
```python
import logging
from typing import Any, Dict, List

from langchain_anthropic import ChatAnthropic
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import Chroma
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


from app.config.settings import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    VECTOR_STORE_TOP_K,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    RETRIEVAL_MODE,
    MMR_DIVERSITY_SCORE
)
from app.config.prompt_templates import SYSTEM_MESSAGES

logger = logging.getLogger(__name__)

class QAChainManager:
    def __init__(self):
        """Initialize QA Chain Manager with custom settings"""
        self.llm = ChatAnthropic(
            model=CLAUDE_MODEL,
            anthropic_api_key=ANTHROPIC_API_KEY,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS
        )
        
        # Initialize empty chat history
        self.chat_memory = ChatMessageHistory()

    def create_qa_chain(self, vector_store: Chroma) -> ConversationalRetrievalChain:
        """Create a conversational retrieval chain"""
        try:
            logger.info("Creating QA chain...")
            
            # Configure retriever
            search_kwargs = {"k": VECTOR_STORE_TOP_K}
            if RETRIEVAL_MODE == "mmr":
                search_kwargs["fetch_k"] = VECTOR_STORE_TOP_K * 2
                search_kwargs["lambda_mult"] = MMR_DIVERSITY_SCORE
            
            retriever = vector_store.as_retriever(
                search_type=RETRIEVAL_MODE,
                search_kwargs=search_kwargs
            )

            # Create the memory
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                output_key="answer",
                return_messages=True
            )

            # Create the QA prompt
            qa_prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_MESSAGES["qa"]),
                ("human", "Using the following context, answer the question. Context: {context}\n\nQuestion: {question}")
            ])

            # Create the conversational chain
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                memory=memory,
                get_chat_history=lambda h: h,  # Just return the history as is
                verbose=True,
                return_source_documents=True
            )

            logger.info(f"QA chain created successfully with {RETRIEVAL_MODE} retrieval")
            return qa_chain

        except Exception as e:
            logger.error(f"Error creating QA chain: {str(e)}")
            logger.error("Exception details:", exc_info=True)
            raise

    def process_query(self, chain: ConversationalRetrievalChain, query: str) -> Dict[str, Any]:
        """Process a query using the QA chain"""
        try:
            if not query or not isinstance(query, str) or not query.strip():
                return {
                    "answer": "Please provide a valid question.",
                    "source_documents": [],
                    "chat_history": []
                }

            # Add the user's question to chat history
            self.chat_memory.add_user_message(query)
            
            # Get current chat history as a list of messages
            current_history = []
            for i in range(0, len(self.chat_memory.messages), 2):
                if i + 1 < len(self.chat_memory.messages):
                    # Add pairs of messages (human and ai)
                    current_history.extend([
                        self.chat_memory.messages[i],
                        self.chat_memory.messages[i + 1]
                    ])

            # Process the query
            result = chain({
                "question": query,
                "chat_history": current_history
            })

            # Extract answer and sources
            answer = result.get("answer", "")
            sources = result.get("source_documents", [])

            # Add the assistant's response to chat history
            if answer:
                self.chat_memory.add_ai_message(answer)

            return {
                "answer": answer or "An error occurred while processing your question.",
                "source_documents": sources,
                "chat_history": self.chat_memory.messages
            }

        except Exception as e:
            logger.error(f"Error in process_query: {str(e)}")
            logger.error("Full exception details:", exc_info=True)
            self.clear_memory()
            return {
                "answer": f"An error occurred while processing your question: {str(e)}",
                "source_documents": [],
                "chat_history": []
            }

    def get_chat_history(self) -> List[BaseMessage]:
        """Get properly formatted chat history"""
        try:
            return self.chat_memory.messages
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return []

    def clear_memory(self) -> None:
        """Clear conversation memory"""
        try:
            self.chat_memory.clear()
            logger.info("Conversation memory cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing memory: {str(e)}")
```

# File: app/core/vector_store.py
```python
# app/core/vector_store.py

import logging
import shutil
import tempfile
import time
from pathlib import Path
from typing import List, Dict, Optional
import atexit

from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import Chroma
from chromadb import PersistentClient, Settings
from langchain_core.documents import Document

# Import DocType from document_processor
from app.core.document_processor import DocType

from app.config.settings import (
    COHERE_API_KEY,
    EMBEDDING_MODEL,
    VECTOR_STORE_SIMILARITY_THRESHOLD,
    VECTOR_STORE_TOP_K,
    ENABLE_CACHE,
    CACHE_DIR,
    MMR_DIVERSITY_SCORE
)

# Configure logging
logger = logging.getLogger(__name__)

class VectorStoreManager:
    _instances = {}
    _temp_dirs = set()
    COLLECTION_NAME = "game_development_docs"
    BATCH_SIZE = 50
    BATCH_DELAY = 2
    
    def __new__(cls, doc_processor=None):
        key = id(doc_processor) if doc_processor else None
        if key not in cls._instances:
            instance = super(VectorStoreManager, cls).__new__(cls)
            instance._initialized = False
            cls._instances[key] = instance
            atexit.register(instance.cleanup_all)
        return cls._instances[key]
    
    def __init__(self, doc_processor=None):
        if not hasattr(self, '_initialized') or not self._initialized:
            self.doc_processor = doc_processor
            self._initialize_store()
            self._initialized = True

    def _initialize_store(self):
        """Initialize the vector store"""
        try:
            self.cleanup_temp_directories()
            
            # Use cache directory if enabled, otherwise use temp directory
            if ENABLE_CACHE:
                self.persist_directory = Path(CACHE_DIR)
                self.persist_directory.mkdir(exist_ok=True)
            else:
                self.persist_directory = Path(tempfile.mkdtemp())
                self._temp_dirs.add(self.persist_directory)
            
            logger.info(f"Using directory for ChromaDB: {self.persist_directory}")
            
            # Initialize embeddings
            self.embeddings = CohereEmbeddings(
                model=EMBEDDING_MODEL,
                cohere_api_key=COHERE_API_KEY
            )
            
            # Initialize ChromaDB client
            self.chroma_client = PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True
                )
            )
            
            logger.info("Vector store initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise

    def get_or_create_vector_store(self, force_recreate: bool = False) -> Chroma:
        """Get existing or create new vector store with incremental updates"""
        if not self.doc_processor:
            raise ValueError("Document processor not set")
            
        try:
            # Load documents
            documents = self.doc_processor.load_documents()
            if not documents:
                raise ValueError("No documents loaded from document processor")
            
            # Create new vector store when force_recreate is True
            if force_recreate:
                logger.info("Force recreating vector store")
                return self.create_vector_store(documents)
            
            try:
                # Try to get existing vector store
                vector_store = Chroma(
                    client=self.chroma_client,
                    collection_name=self.COLLECTION_NAME,
                    embedding_function=self.embeddings
                )
                
                # Get existing document IDs
                collection = self.chroma_client.get_collection(self.COLLECTION_NAME)
                existing_ids = set(collection.get()['ids'])
                
                # Process new documents in batches
                new_docs = []
                for doc in documents:
                    doc_id = f"{doc.metadata['source']}_{hash(doc.page_content)}"
                    if doc_id not in existing_ids:
                        new_docs.append(doc)
                
                if new_docs:
                    logger.info(f"Found {len(new_docs)} new documents to add")
                    # Process new documents in batches
                    for i in range(0, len(new_docs), self.BATCH_SIZE):
                        batch = new_docs[i:i + self.BATCH_SIZE]
                        texts = [doc.page_content for doc in batch]
                        metadatas = [doc.metadata for doc in batch]
                        vector_store.add_texts(texts=texts, metadatas=metadatas)
                        
                        if i + self.BATCH_SIZE < len(new_docs):
                            time.sleep(self.BATCH_DELAY)
                
                return vector_store
                
            except Exception as e:
                logger.warning(f"Error accessing existing vector store: {e}")
                logger.info("Creating new vector store")
                return self.create_vector_store(documents)
                
        except Exception as e:
            logger.error(f"Error in get_or_create_vector_store: {str(e)}")

    def create_vector_store(self, documents: List[Document]) -> Chroma:
        """Create a new vector store with batched processing"""
        try:
            if not documents:
                logger.warning("No documents provided to create vector store")
                return None

            # Reset the client to clear any existing collections
            self.chroma_client.reset()
            
            logger.info(f"Creating new vector store with {len(documents)} documents")
            
            # Create new Chroma vector store
            vector_store = None
            for i in range(0, len(documents), self.BATCH_SIZE):
                batch = documents[i:i + self.BATCH_SIZE]
                logger.info(f"Processing batch {i//self.BATCH_SIZE + 1} of {len(documents)//self.BATCH_SIZE + 1}")
                
                if vector_store is None:
                    # Create initial vector store with first batch
                    vector_store = Chroma.from_documents(
                        documents=batch,
                        embedding=self.embeddings,
                        client=self.chroma_client,
                        collection_name=self.COLLECTION_NAME
                    )
                else:
                    # Add subsequent batches
                    texts = [doc.page_content for doc in batch]
                    metadatas = [doc.metadata for doc in batch]
                    vector_store.add_texts(texts=texts, metadatas=metadatas)
                
                # Add delay between batches to respect rate limits
                if i + self.BATCH_SIZE < len(documents):
                    time.sleep(self.BATCH_DELAY)
            
            logger.info(f"Successfully created vector store with {len(documents)} documents")
            return vector_store
                
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            raise

    def get_context_for_query(self, query: str, is_code_generation: bool = False) -> Dict[str, List[Document]]:
        """Get relevant context based on query type"""
        try:
            if is_code_generation:
                return self._get_code_generation_context(query)
            return self._get_general_query_context(query)
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            raise

    def _get_code_generation_context(self, query: str) -> Dict[str, List[Document]]:
        """Multi-phase retrieval for code generation"""
        try:
            logger.info("Retrieving context for code generation query")
            
            # 1. Always get rules (smaller k as rules should be concise)
            rules = self.similarity_search_with_filter(
                query, 
                {"doc_type": DocType.RULESET.value},
                k=2
            )
            logger.debug(f"Retrieved {len(rules)} rule documents")
            
            # 2. Always check limitations
            limitations = self.similarity_search_with_filter(
                query,
                {"doc_type": DocType.LIMITATIONS.value},
                k=2
            )
            logger.debug(f"Retrieved {len(limitations)} limitation documents")
            
            # 3. Get relevant function definitions
            functions = self.similarity_search_with_filter(
                query,
                {"doc_type": DocType.FUNCTIONS.value},
                k=3
            )
            logger.debug(f"Retrieved {len(functions)} function documents")
            
            # 4. Find similar examples
            examples = self.similarity_search_with_filter(
                query,
                {"doc_type": DocType.EXAMPLE.value},
                k=3
            )
            logger.debug(f"Retrieved {len(examples)} example documents")
            
            context = {
                "rules": rules,
                "limitations": limitations,
                "functions": functions,
                "examples": examples
            }
            
            logger.info("Successfully retrieved all context for code generation")
            return context
            
        except Exception as e:
            logger.error(f"Error in code generation context retrieval: {str(e)}")
            raise

    def _get_general_query_context(self, query: str) -> Dict[str, List[Document]]:
        """Context retrieval for general questions"""
        try:
            logger.info("Retrieving context for general query")
            
            # Prioritize rules, limitations, and functions for general queries
            rules = self.similarity_search_with_filter(
                query,
                {"doc_type": DocType.RULESET.value},
                k=2
            )
            
            limitations = self.similarity_search_with_filter(
                query,
                {"doc_type": DocType.LIMITATIONS.value},
                k=2
            )
            
            functions = self.similarity_search_with_filter(
                query,
                {"doc_type": DocType.FUNCTIONS.value},
                k=4
            )
            
            context = {
                "rules": rules,
                "limitations": limitations,
                "functions": functions
            }
            
            logger.info("Successfully retrieved context for general query")
            return context
            
        except Exception as e:
            logger.error(f"Error in general context retrieval: {str(e)}")
            raise

    def similarity_search_with_filter(
        self, 
        query: str, 
        filter_dict: Dict, 
        k: int = 4,
        fetch_k: Optional[int] = None
    ) -> List[Document]:
        """Perform similarity search with metadata filtering"""
        try:
            collection = self.chroma_client.get_collection(name=self.COLLECTION_NAME)
            
            # For MMR, fetch more candidates
            if fetch_k is None:
                fetch_k = k * 2
            
            # Convert filter dict to Chroma filter format
            where = {f"metadata.{key}": value for key, value in filter_dict.items()}
            
            results = collection.query(
                query_texts=[query],
                n_results=k,
                where=where,
                include=["documents", "metadatas"]
            )
            
            # Convert results to Document objects
            documents = []
            for i in range(len(results['documents'][0])):
                doc = Document(
                    page_content=results['documents'][0][i],
                    metadata=results['metadatas'][0][i]
                )
                documents.append(doc)
            
            logger.debug(f"Found {len(documents)} documents matching filter {filter_dict}")
            return documents
            
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            raise

    def cleanup_temp_directories(self):
        """Clean up any temporary ChromaDB directories"""
        try:
            temp_dir = Path(tempfile.gettempdir())
            logger.info(f"Scanning for temporary directories in: {temp_dir}")
            
            # Clean up tracked directories
            for temp_path in self._temp_dirs.copy():
                if temp_path.exists():
                    try:
                        shutil.rmtree(str(temp_path))
                        self._temp_dirs.remove(temp_path)
                        logger.info(f"Cleaned up tracked temporary directory: {temp_path}")
                    except Exception as e:
                        logger.warning(f"Failed to clean up tracked directory {temp_path}: {e}")
            
            # Clean up untracked directories
            for item in temp_dir.glob("tmp*"):
                if item.is_dir():
                    try:
                        if any(f.name == 'chroma.sqlite3' for f in item.glob('*')) or \
                           any(f.name == 'index' for f in item.glob('*')):
                            shutil.rmtree(str(item))
                            logger.info(f"Cleaned up untracked ChromaDB directory: {item}")
                    except Exception as e:
                        logger.warning(f"Failed to clean up directory {item}: {e}")
                        
        except Exception as e:
            logger.error(f"Error cleaning up temporary directories: {e}")

    def cleanup_all(self):
        """Cleanup method called on system exit"""
        logger.info("Performing final cleanup...")
        try:
            self.cleanup_temp_directories()
            if hasattr(self, 'chroma_client'):
                self.chroma_client.reset()
            logger.info("Final cleanup completed")
        except Exception as e:
            logger.error(f"Error during final cleanup: {str(e)}")
```

# File: app/config/__init__.py
```python

```

# File: app/config/prompt_templates.py
```python
# app/config/prompt_templates.py

from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)

# System messages for different components
SYSTEM_MESSAGES = {
    "qa": """You are a T# programming expert assistant. Your role is to:
1. Help developers write correct T# code by analyzing similar examples
2. Explain Terra Studio concepts clearly with reference to documentation
3. Highlight differences between T# and Unity C#
4. Provide practical, working examples based on patterns

When responding to code generation requests:
- Analyze provided example game mechanics for relevant patterns
- Apply T# programming rules from the documentation
- Combine patterns to create new solutions
- Include detailed comments explaining the implementation
- Focus on T#-specific features and best practices

Use the context below to:
1. First identify relevant example implementations
2. Extract key patterns and approaches
3. Apply T# rules and conventions
4. Generate new code that combines these elements

If you can't find specific examples or rules in the context, 
be honest about it and provide general T# guidance.""",
    
    "summarization": """You are a technical documentation analyzer for T# programming language.
Your task is to create clear, structured summaries that:
1. Identify core concepts and functionality
2. Highlight key differences from Unity C#
3. Extract important code patterns and examples
4. Note common usage scenarios and best practices""",
    
    "error_handling": """You are a T# debugging assistant. Your role is to:
1. Identify common T# programming errors
2. Explain why errors occur in T# context
3. Provide correct solutions with examples
4. Suggest best practices to avoid similar issues"""
}

# QA Chain Prompts
qa_messages = [
    SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGES["qa"]),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template(
        "Available Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Please provide a detailed answer that references relevant examples and documentation:"
    )
]

QA_PROMPT = ChatPromptTemplate.from_messages(qa_messages)

# Summarization Chain Prompts
summarization_messages = [
    SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGES["summarization"]),
    HumanMessagePromptTemplate.from_template("""Please analyze this T# documentation:
{text}

Create a structured summary that includes:
1. Core Functionality:
   - Main purpose
   - Key features
   - Usage scenarios

2. T# Specifics:
   - Differences from Unity C#
   - Unique Terra Studio features
   - Implementation details

3. Code Patterns:
   - Common usage examples
   - Best practices
   - Typical patterns

4. Integration Points:
   - How it fits with other T# components
   - Common integration patterns
   - Compatibility considerations

Summary:""")
]

SUMMARY_PROMPT = ChatPromptTemplate.from_messages(summarization_messages)

# Error Handling Chain Prompts
error_handling_messages = [
    SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGES["error_handling"]),
    HumanMessagePromptTemplate.from_template("""Error Context:
{error_context}

Error Message: {error_message}

Please provide:
1. Error explanation in T# context
2. Potential causes
3. Solution with code example
4. Prevention tips

Response:""")
]

ERROR_HANDLING_PROMPT = ChatPromptTemplate.from_messages(error_handling_messages)

# Retrieval Prompts
RETRIEVAL_PROMPT = """Given these documents about T# programming:
{documents}

Please find information relevant to:
{query}

Focus on:
1. Exact matches to the query
2. Related T# concepts
3. Relevant code examples
4. Implementation details"""

# You can add more specialized prompts as needed
VALIDATION_PROMPT = """Validate this T# code snippet:
{code}

Check for:
1. T# syntax correctness
2. Terra Studio compatibility
3. Best practice adherence
4. Potential issues"""

# Export all prompts as a dictionary for easy access
PROMPT_TEMPLATES = {
    "qa": QA_PROMPT,
    "summary": SUMMARY_PROMPT,
    "error": ERROR_HANDLING_PROMPT,
    "retrieval": RETRIEVAL_PROMPT,
    "validation": VALIDATION_PROMPT
}
```

# File: app/config/settings.py
```python
# File: app/config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Application settings
DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
ALLOWED_ORIGIN = os.getenv('ALLOWED_ORIGIN', 'http://localhost:3000')

# Vector store settings
VECTOR_STORE_SIMILARITY_THRESHOLD = float(os.getenv('VECTOR_STORE_SIMILARITY_THRESHOLD', '0.3'))
VECTOR_STORE_TOP_K = int(os.getenv('VECTOR_STORE_TOP_K', '8'))

# Embedding settings
EMBEDDING_MODEL = os.getenv('COHERE_MODEL', 'embed-multilingual-v2.0')

# LLM settings
CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-sonnet-20240229')
LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.3'))
LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', '4096'))

# Chunking settings
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '2000'))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '400'))

# Retrieval settings
RETRIEVAL_MODE = os.getenv('RETRIEVAL_MODE', 'mmr')  # 'similarity' or 'mmr'
MMR_DIVERSITY_SCORE = float(os.getenv('MMR_DIVERSITY_SCORE', '0.3'))

# Cache settings
ENABLE_CACHE = os.getenv('ENABLE_CACHE', 'True').lower() in ('true', '1', 't')
CACHE_DIR = os.getenv('CACHE_DIR', '.cache')

# Document processing settings
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
RETRY_DELAY = float(os.getenv('RETRY_DELAY', '1.0'))
MIN_CHUNK_SIZE = int(os.getenv('MIN_CHUNK_SIZE', '100'))
MAX_CHUNK_SIZE = int(os.getenv('MAX_CHUNK_SIZE', '3000'))
```

# File: app/utils/__init__.py
```python

```

# File: app/utils/llm_test.py
```python
import logging
from app.config.settings import ANTHROPIC_API_KEY
from langchain_anthropic import ChatAnthropic

logger = logging.getLogger(__name__)

def test_llm():
    """Test the LLM connection and basic functionality"""
    try:
        llm = ChatAnthropic(
            model_name="claude-3-sonnet-20240229",
            anthropic_api_key=ANTHROPIC_API_KEY,
            temperature=0
        )
        response = llm.invoke("Say 'test successful' if you can read this.")
        
        if "test successful" in response.content.lower():
            logger.info("LLM test successful")
            return True
        else:
            logger.error("LLM test failed - unexpected response")
            return False
            
    except Exception as e:
        logger.error(f"LLM test failed with error: {str(e)}")
        return False
```

# File: app/utils/text_splitter.py
```python
# app/utils/text_splitter.py

import re
from typing import List
from langchain.text_splitter import TextSplitter
from langchain.schema import Document

class CustomMarkdownSplitter(TextSplitter):
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        super().__init__()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.markdown_header_pattern = re.compile(r'^#+\s+')
        self.code_block_pattern = re.compile(r'```[\s\S]*?```')

    def split_text(self, text: str) -> List[str]:
        if not text.strip():
            return []

        # First, identify and preserve code blocks
        code_blocks = {}
        code_block_count = 0
        
        def replace_code_block(match):
            nonlocal code_block_count
            placeholder = f"CODE_BLOCK_{code_block_count}"
            code_blocks[placeholder] = match.group(0)
            code_block_count += 1
            return placeholder

        text_with_placeholders = self.code_block_pattern.sub(replace_code_block, text)

        # Split into sections at headers
        sections = []
        current_section = []
        lines = text_with_placeholders.split('\n')

        for line in lines:
            if self.markdown_header_pattern.match(line) and current_section:
                sections.append('\n'.join(current_section))
                current_section = []
            current_section.append(line)

        if current_section:
            sections.append('\n'.join(current_section))

        # Process each section while respecting chunk size
        chunks = []
        for section in sections:
            current_chunk = []
            current_size = 0
            
            for line in section.split('\n'):
                line_size = len(line) + 1  # +1 for newline
                
                if current_size + line_size > self.chunk_size and current_chunk:
                    chunk_text = '\n'.join(current_chunk).strip()
                    if chunk_text:
                        chunks.append(chunk_text)
                    current_chunk = []
                    current_size = 0
                    
                    # Add overlap from previous chunk
                    if self.chunk_overlap > 0:
                        overlap_lines = []
                        overlap_size = 0
                        for prev_line in reversed(current_chunk):
                            if overlap_size + len(prev_line) + 1 > self.chunk_overlap:
                                break
                            overlap_lines.insert(0, prev_line)
                            overlap_size += len(prev_line) + 1
                        current_chunk = overlap_lines
                        current_size = overlap_size

                current_chunk.append(line)
                current_size += line_size

            if current_chunk:
                chunk_text = '\n'.join(current_chunk).strip()
                if chunk_text:
                    chunks.append(chunk_text)

        # Restore code blocks in chunks
        restored_chunks = []
        for chunk in chunks:
            restored_text = chunk
            for placeholder, code_block in code_blocks.items():
                restored_text = restored_text.replace(placeholder, code_block)
            restored_chunks.append(restored_text)

        return restored_chunks

    def create_documents(self, texts: List[str], metadatas: List[dict] = None) -> List[Document]:
        """Create documents from a list of texts."""
        _metadatas = metadatas or [{}] * len(texts)
        return [
            Document(page_content=text, metadata=metadata)
            for text, metadata in zip(texts, _metadatas)
            if text.strip()  # Only create documents for non-empty texts
        ]

    def split_documents(self, documents: List[dict]) -> List[Document]:
        """Split documents."""
        texts = []
        metadatas = []
        for doc in documents:
            split_texts = self.split_text(doc["page_content"])
            texts.extend(split_texts)
            metadatas.extend([doc["metadata"]] * len(split_texts))
        return self.create_documents(texts, metadatas)
```

# File: app/utils/validators.py
```python
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
```

# File: app/utils/version_check.py
```python
import logging
import pkg_resources
from packaging import version

logger = logging.getLogger(__name__)

REQUIRED_VERSIONS = {
    'flask': '2.3.2',
    'flask-cors': '3.0.10',
    'python-dotenv': '1.0.0',
    'pydantic': '1.10.18',
    'anthropic': '0.17.0',
    'langsmith': '0.0.87',
    'langchain-core': '0.1.23',
    'langchain': '0.0.311',
    'langchain-anthropic': '0.1.1',
    'langchain-community': '0.0.13',
    'chromadb': '0.3.29',
    'cohere': '4.37',
    'gunicorn': '20.1.0',
    'tiktoken': '0.8.0',  # Updated to match your installed version
    'pypdf': '3.9.0'
}

def check_versions():
    """Check if installed package versions meet minimum requirements"""
    mismatched = []
    missing = []
    
    for package, required_version in REQUIRED_VERSIONS.items():
        try:
            installed_version = pkg_resources.get_distribution(package).version
            if version.parse(installed_version) < version.parse(required_version):
                mismatched.append(f"{package}: required>={required_version}, installed={installed_version}")
        except pkg_resources.DistributionNotFound:
            missing.append(package)
    
    if missing:
        logger.warning(f"Missing packages: {', '.join(missing)}")
    if mismatched:
        logger.warning("Version mismatches found:")
        for mismatch in mismatched:
            logger.warning(mismatch)
    
    return not (missing or mismatched)
```

# File: app/api/routes.py
```python
# app/api/routes.py

from flask import Blueprint, request, jsonify
import logging
from app.core.initializer import AppComponents

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)

@api_bp.route('/ask', methods=['POST', 'OPTIONS'])
def ask_question():
    if request.method == 'OPTIONS':
        return handle_options_request()
    
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        question = data.get('question', '').strip()
        if not question:
            return jsonify({"error": "Question cannot be empty"}), 400
            
        logger.info(f"Received question: {question}")
        
        if AppComponents.qa_chain is None:
            logger.error("QA chain is not initialized")
            return jsonify({"error": "Service not ready. Please try again later."}), 503
        
        result = AppComponents.qa_chain_manager.process_query(AppComponents.qa_chain, question)
        
        response = {
            "answer": result["answer"],
            "sources": [doc.metadata.get('source', 'Unknown') for doc in result.get('source_documents', [])],
        }
        
        logger.info(f"Generated answer successfully for question: {question}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", exc_info=True)
        return jsonify({
            "error": "An error occurred while processing your question.",
            "details": str(e) if isinstance(e, ValueError) else None
        }), 500

def handle_options_request():
    response = jsonify({'message': 'OK'})
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST')
    return response
```

# File: scripts/__init__.py
```python

```

# File: scripts/generate_summaries.py
```python
import logging
import sys
from pathlib import Path

# Add the project root to Python path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from app.core.document_processor import DocumentProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_summaries():
    """Generate and save document summaries"""
    try:
        # Setup paths
        base_path = Path(__file__).parent.parent
        knowledge_base_path = base_path / "data" / "knowledge_base"
        summaries_path = base_path / "data" / "summaries"
        
        # Ensure directories exist
        knowledge_base_path.mkdir(exist_ok=True, parents=True)
        summaries_path.mkdir(exist_ok=True, parents=True)
        
        logger.info("Initializing document processor...")
        doc_processor = DocumentProcessor(
            knowledge_base_path=str(knowledge_base_path),
            summaries_path=str(summaries_path)
        )
        
        logger.info("Generating summaries...")
        summaries = doc_processor.generate_summaries()
        logger.info(f"Successfully generated {len(summaries)} summaries")
        
    except Exception as e:
        logger.error(f"Error generating summaries: {str(e)}")
        raise

if __name__ == "__main__":
    generate_summaries()
```

# File: scripts/recreate_vector_store.py
```python
import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import logging
from app.main import create_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def recreate_vector_store():
    """Utility script to recreate the vector store"""
    logger.info("Recreating vector store...")
    try:
        app = create_app(force_recreate=True)
        with app.app_context():
            logger.info("Vector store recreation completed successfully")
    except Exception as e:
        logger.error(f"Failed to recreate vector store: {str(e)}")
        raise

if __name__ == "__main__":
    recreate_vector_store()
```

# File: tests/__Init__.py
```python

```

# File: tests/unit/__init__.py
```python

```

# File: tests/unit/test_anthropic.py
```python
# app/tests/unit/test_anthropic.py

import unittest
import logging
import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from app.config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestAnthropicChain(unittest.TestCase):
    """Test cases for ChatAnthropic functionality"""

    def setUp(self):
        """Set up test environment before each test"""
        self.llm = ChatAnthropic(
            model=CLAUDE_MODEL,
            anthropic_api_key=ANTHROPIC_API_KEY,
            temperature=0
        )

    def test_model_direct(self):
        """Test ChatAnthropic directly without chain"""
        try:
            response = self.llm.invoke("Say 'test successful' if you can read this.")
            logger.info(f"Direct model test result: {response}")
            self.assertIsNotNone(response)
        except Exception as e:
            logger.error(f"Direct model test failed: {str(e)}")
            raise

    def test_chat_messages(self):
        """Test ChatAnthropic with chat messages"""
        try:
            messages = [
                SystemMessage(content="You are a helpful assistant."),
                HumanMessage(content="Say 'test successful' if you can read this.")
            ]
            response = self.llm.invoke(messages)
            logger.info(f"Chat message test result: {response}")
            self.assertIsNotNone(response)
        except Exception as e:
            logger.error(f"Chat message test failed: {str(e)}")
            raise

    def test_simple_chain(self):
        """Test simple chain with ChatAnthropic"""
        try:
            # Create a chat prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant."),
                ("human", "{input}")
            ])
            
            chain = prompt | self.llm
            
            result = chain.invoke({"input": "Say 'test successful' if you can read this."})
            logger.info(f"Simple chain test result: {result}")
            self.assertIsNotNone(result)
        except Exception as e:
            logger.error(f"Simple chain test failed: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            raise

def print_package_versions():
    """Print relevant package versions"""
    import pkg_resources
    packages = [
        'langchain',
        'langchain-anthropic',
        'langchain-core',
        'langchain-community',
        'anthropic'
    ]
    
    logger.info("\nInstalled package versions:")
    for package in packages:
        try:
            version = pkg_resources.get_distribution(package).version
            logger.info(f"{package}: {version}")
        except pkg_resources.DistributionNotFound:
            logger.warning(f"{package} not found")

if __name__ == '__main__':
    print_package_versions()
    unittest.main(verbosity=2)
```

# File: tests/unit/test_components.py
```python
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
```

# File: tests/unit/test_qa_chain.py
```python
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
```

# File: tests/integration/test_integration.py
```python
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
```
