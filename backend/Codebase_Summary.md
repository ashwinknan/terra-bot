# RAG Chatbot Implementation Documentation

This document describes the code for a RAG chatbot and how the files are organized. Below you'll find the complete source code and structure of the implementation.

## Complete Directory Structure
```
└── backend
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
    │   │   ├── Accessing Components & Game Objects.md
    │   │   ├── Adding Audio in T#.md
    │   │   ├── Adding Haptics.md
    │   │   ├── Limitations of T#.md
    │   │   ├── Loading Scenes.md
    │   │   ├── Mountrain Climber Controller_documentation.md
    │   │   ├── Particles in T#.md
    │   │   ├── SpaceMarshal_documentation.md
    │   │   ├── StudioAnalytics.md
    │   │   ├── StudioExtensions.md
    │   │   ├── StudioLeaderboard.md
    │   │   ├── StudioPrefs.md
    │   │   ├── StudioUser.md
    │   │   ├── T# Basics.md
    │   │   ├── T# Coroutines.md
    │   │   ├── T# Event Functions.md
    │   │   ├── T# Variables.md
    │   │   ├── Traffic Rider Controller_documentation.md
    │   │   ├── Working with the Player in T#.md
    │   │   └── World War Controller_documentation.md
    │   ├── summaries
    │   │   └── summaries.json
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
import logging
from pathlib import Path
import json
from typing import Dict, List
from dataclasses import dataclass

from langchain_anthropic import ChatAnthropic
from langchain_core.documents import Document
from app.config.prompt_templates import PROMPT_TEMPLATES
from app.config.settings import (
    ANTHROPIC_API_KEY, 
    CHUNK_SIZE, 
    CHUNK_OVERLAP,
    CLAUDE_MODEL,
    LLM_TEMPERATURE
)
from app.utils.text_splitter import CustomMarkdownSplitter

logger = logging.getLogger(__name__)

@dataclass
class DocumentMetadata:
    source: str
    type: str

class DocumentProcessor:
    def __init__(self, knowledge_base_path: str, summaries_path: str):
        """Initialize document processor with improved configuration"""
        self.knowledge_base_path = Path(knowledge_base_path)
        self.summaries_path = Path(summaries_path)
        self.llm = ChatAnthropic(
            model=CLAUDE_MODEL,
            anthropic_api_key=ANTHROPIC_API_KEY,
            temperature=LLM_TEMPERATURE
        )
        self.custom_splitter = CustomMarkdownSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
    
    def load_documents(self) -> List[Document]:
        """Load and process documents with improved error handling"""
        documents = []
        logger.info(f"Loading documents from {self.knowledge_base_path}")
        
        try:
            for file_path in self.knowledge_base_path.glob('*'):
                if file_path.suffix == '.md':
                    logger.info(f"Processing Markdown: {file_path.name}")
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        chunks = self.custom_splitter.split_text(content)
                        
                        # Validate and process each chunk
                        for chunk in chunks:
                            if chunk.strip():  # Skip empty chunks
                                doc = Document(
                                    page_content=chunk,
                                    metadata=DocumentMetadata(
                                        source=file_path.name,
                                        type='markdown'
                                    ).__dict__
                                )
                                documents.append(doc)
                                
                        logger.info(f"Successfully processed {file_path.name}")
                    except Exception as e:
                        logger.error(f"Error processing {file_path.name}: {str(e)}")
                else:
                    logger.warning(f"Skipping unsupported file: {file_path.name}")
                    
            if not documents:
                raise ValueError("No valid documents found in knowledge base")
                
            logger.info(f"Successfully loaded {len(documents)} document chunks")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            raise
    
    def generate_summaries(self) -> Dict[str, str]:
        """Generate improved document summaries using predefined prompts"""
        summaries = {}
        logger.info("Generating document summaries")
        
        try:
            for file_path in self.knowledge_base_path.glob('*.md'):
                logger.info(f"Summarizing {file_path.name}")
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    # Use summary prompt template
                    response = self.llm.invoke(
                        PROMPT_TEMPLATES["summary"].format(text=content)
                    )
                    
                    summary = response.content if hasattr(response, 'content') else str(response)
                    summaries[file_path.stem] = summary
                    logger.info(f"Successfully summarized {file_path.name}")
                    
                except Exception as e:
                    logger.error(f"Error summarizing {file_path.name}: {str(e)}")
            
            if not summaries:
                raise ValueError("No summaries generated")
            
            # Save summaries
            self.save_summaries(summaries)
            logger.info(f"Generated and saved {len(summaries)} summaries")
            return summaries
            
        except Exception as e:
            logger.error(f"Error generating summaries: {str(e)}")
            raise

    def save_summaries(self, summaries: Dict[str, str]) -> None:
        """Save summaries to file"""
        try:
            # Create summaries directory if it doesn't exist
            self.summaries_path.mkdir(exist_ok=True, parents=True)
            
            # Save summaries with proper formatting
            summary_file = self.summaries_path / "summaries.json"
            with summary_file.open('w', encoding='utf-8') as f:
                json.dump(summaries, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Summaries saved to {summary_file}")
            
        except Exception as e:
            logger.error(f"Error saving summaries: {str(e)}")
            raise
    
    def load_summaries(self) -> Dict[str, str]:
        """Load existing summaries with validation"""
        try:
            summary_file = self.summaries_path / "summaries.json"
            if not summary_file.exists():
                logger.warning("No existing summaries found, generating new ones")
                return self.generate_summaries()
                
            with summary_file.open('r', encoding='utf-8') as f:
                summaries = json.load(f)
                
            if not summaries:
                logger.warning("Empty summaries file found, generating new ones")
                return self.generate_summaries()
                
            logger.info(f"Loaded {len(summaries)} existing summaries")
            return summaries
            
        except Exception as e:
            logger.error(f"Error loading summaries: {str(e)}")
            raise
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
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        
    Returns:
        Result of the function call
        
    Raises:
        Exception: If all retry attempts fail
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

def _safe_generate_summaries(doc_processor):
    """
    Safely generate summaries with proper error handling
    
    Args:
        doc_processor: DocumentProcessor instance
        
    Returns:
        Dict of generated summaries
    """
    try:
        return doc_processor.generate_summaries()
    except Exception as e:
        logger.error(f"Error generating summaries: {str(e)}")
        # Return empty dict if generation fails
        return {}

def initialize_app(force_recreate=False):
    """
    Initialize all application components with improved error handling and retries
    """
    try:
        logger.info("Starting application initialization...")
        
        # Setup paths
        base_path = Path(__file__).parent.parent.parent
        knowledge_base_path = base_path / "data" / "knowledge_base"
        summaries_path = base_path / "data" / "summaries"
        
        # Ensure directories exist
        knowledge_base_path.mkdir(exist_ok=True, parents=True)
        summaries_path.mkdir(exist_ok=True, parents=True)
        
        # Initialize document processor
        logger.info("Initializing document processor...")
        AppComponents.doc_processor = DocumentProcessor(
            knowledge_base_path=str(knowledge_base_path),
            summaries_path=str(summaries_path)
        )
        
        # Initialize vector store manager with doc processor
        logger.info("Initializing vector store manager...")
        AppComponents.vector_store_manager = VectorStoreManager(doc_processor=AppComponents.doc_processor)
        
        # Load existing summaries only - don't regenerate
        logger.info("Loading existing summaries...")
        try:
            summaries = AppComponents.doc_processor.load_summaries()
            if not summaries and force_recreate:
                logger.warning("No summaries found and force_recreate=True, generating new ones...")
                summaries = _retry_with_backoff(
                    lambda: _safe_generate_summaries(AppComponents.doc_processor)
                )
            elif not summaries:
                logger.error("No summaries found. Please run generate_summaries.py first")
                raise RuntimeError("Missing summaries - run generate_summaries.py first")
                
            logger.info(f"Successfully loaded {len(summaries)} summaries")
        except FileNotFoundError:
            logger.error("Summaries file not found. Please run generate_summaries.py first")
            raise RuntimeError("Missing summaries - run generate_summaries.py first")
        
        # Initialize vector store
        logger.info("Initializing vector store...")
        AppComponents.vector_store = _retry_with_backoff(
            lambda: AppComponents.vector_store_manager.get_or_create_vector_store(
                force_recreate=force_recreate,
                summaries=summaries
            )
        )

        # Initialize QA chain manager and create chain
        logger.info("Initializing QA chain...")
        AppComponents.qa_chain_manager = QAChainManager()
        AppComponents.qa_chain = AppComponents.qa_chain_manager.create_qa_chain(
            AppComponents.vector_store
        )
        
        logger.info("Application initialized successfully")
        
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
# app/core/qa_chain.py
import logging
from typing import Any, Dict, List, Optional

from langchain_anthropic import ChatAnthropic
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import Chroma
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
)

from app.config.settings import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    VECTOR_STORE_TOP_K,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    RETRIEVAL_MODE,
    MMR_DIVERSITY_SCORE
)
from app.config.prompt_templates import SYSTEM_MESSAGES, QA_PROMPT

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
        
        # Initialize memory with correct configuration
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
            input_key="question"
        )
        
        # Explicitly initialize empty chat history
        self.memory.chat_memory.messages = []
        
        # Use the imported prompt template
        self.qa_prompt = QA_PROMPT

    def create_qa_chain(self, vector_store: Chroma) -> ConversationalRetrievalChain:
        try:
            logger.info("Creating QA chain...")
            logger.info(f"SYSTEM_MESSAGES contents: {SYSTEM_MESSAGES}")  # Add this debug line
            
            # Configure retriever with explicit search type
            search_kwargs = {
                "k": VECTOR_STORE_TOP_K,
            }
            
            if RETRIEVAL_MODE == "mmr":
                search_kwargs["fetch_k"] = VECTOR_STORE_TOP_K * 2
                search_kwargs["lambda_mult"] = MMR_DIVERSITY_SCORE
                retriever = vector_store.as_retriever(
                    search_type="mmr",
                    search_kwargs=search_kwargs
                )
            else:
                retriever = vector_store.as_retriever(
                    search_type="similarity",
                    search_kwargs=search_kwargs
                )

            logger.info("Creating chain with QA_PROMPT...")
            # Create the chain using QA_PROMPT from prompt_templates
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                memory=self.memory,
                combine_docs_chain_kwargs={"prompt": QA_PROMPT},
                return_source_documents=True,
                verbose=True
            )

            logger.info(f"QA chain created successfully with {RETRIEVAL_MODE} retrieval")
            return qa_chain

        except Exception as e:
            logger.error(f"Error creating QA chain: {str(e)}")
            logger.error("Exception details:", exc_info=True)  # Add full exception details
            raise

    def process_query(self, chain: ConversationalRetrievalChain, query: str) -> Dict[str, Any]:
        try:
            if not query.strip():
                return {
                    "answer": "Please provide a valid question.",
                    "source_documents": [],
                    "chat_history": []
                }

            # Use the chain's invoke method instead of calling it directly
            result = chain.invoke({
                "question": query
            })

            # Extract the answer and sources
            answer = result.get("answer", "")
            sources = result.get("source_documents", [])

            # Update memory if we got a valid answer
            if answer.strip():
                self.memory.chat_memory.add_user_message(query)
                self.memory.chat_memory.add_ai_message(answer)

            return {
                "answer": answer,
                "source_documents": sources,
                "chat_history": self.get_chat_history()
            }

        except Exception as e:
            logger.error(f"Error in process_query: {str(e)}")
            # Clear memory in case of error
            self.clear_memory()
            return {
                "answer": "An error occurred while processing your question.",
                "source_documents": [],
                "chat_history": []
            }

    def get_chat_history(self) -> List[BaseMessage]:
        """Get properly formatted chat history"""
        try:
            if not self.memory or not self.memory.chat_memory:
                return []
                
            messages = self.memory.chat_memory.messages
            if not all(isinstance(msg, BaseMessage) for msg in messages):
                self.clear_memory()
                return []
                
            return messages
            
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return []

    def clear_memory(self) -> None:
        """Clear conversation memory"""
        try:
            if self.memory:
                self.memory.clear()
                self.memory.chat_memory.messages = []
            logger.info("Conversation memory cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing memory: {str(e)}")
```

# File: app/core/vector_store.py
```python
# app/core/vector_store.py
from pathlib import Path
import os
import shutil
import logging
import tempfile
import atexit
import warnings
import numpy as np
import time
import hashlib
from typing import List, Optional, Dict
import contextlib

from langchain_cohere import CohereEmbeddings
from langchain_chroma import Chroma
from chromadb import PersistentClient, Settings
import chromadb
from langchain_core.documents import Document

from app.config.settings import (
    COHERE_API_KEY,
    EMBEDDING_MODEL,
    VECTOR_STORE_SIMILARITY_THRESHOLD,
    VECTOR_STORE_TOP_K,
    ENABLE_CACHE,
    CACHE_DIR
)

# Configure logging
logging.getLogger('chromadb').setLevel(logging.WARNING)
logging.getLogger('cohere').setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

@contextlib.contextmanager
def suppress_stdout():
    """Context manager to suppress stdout temporarily"""
    import sys
    import os
    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    try:
        yield
    finally:
        sys.stdout = original_stdout

class VectorStoreManager:
    _instances = {}
    _temp_dirs = set()
    COLLECTION_NAME = "game_development_docs"
    BATCH_SIZE = 50  # Size of batches for document processing
    BATCH_DELAY = 2  # Delay between batches in seconds
    
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
            
            # Initialize ChromaDB client with updated settings
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=chromadb.Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True
                )
            )
                
            logger.info("Vector store initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise

    def _get_document_hashes(self, documents: List[Document]) -> Dict[str, str]:
        """Create hashes for documents to track changes"""
        return {
            doc.metadata['source']: hashlib.md5(
                doc.page_content.encode()
            ).hexdigest() 
            for doc in documents
        }

    def _store_document_hashes(self, collection, hashes: Dict[str, str]):
        """Store document hashes in collection metadata using the correct API"""
        try:
            metadata = collection.get()["metadata"] or {}
            metadata["document_hashes"] = hashes
            collection.modify(metadata=metadata)
            logger.info("Successfully stored document hashes in collection metadata")
        except Exception as e:
            logger.warning(f"Failed to store document hashes: {str(e)}")

    def _load_existing_hashes(self) -> Dict[str, str]:
        """Load existing document hashes from store metadata"""
        try:
            collection = self.chroma_client.get_collection(self.COLLECTION_NAME)
            metadata = collection.get()["metadata"]
            return metadata.get('document_hashes', {}) if metadata else {}
        except Exception as e:
            logger.warning(f"Failed to load existing hashes: {str(e)}")
            return {}

    def get_vector_store(self) -> Chroma:
        """Get a LangChain Chroma instance for the current vector store"""
        try:
            return Chroma(
                client=self.chroma_client,
                collection_name=self.COLLECTION_NAME,
                embedding_function=self.embeddings
            )
        except Exception as e:
            logger.error(f"Error getting vector store: {str(e)}")
            raise

    def similarity_search(self, query: str, k: int = None, threshold: float = None):
        """Enhanced similarity search using LangChain's Chroma wrapper"""
        try:
            k = k or VECTOR_STORE_TOP_K
            threshold = threshold or VECTOR_STORE_SIMILARITY_THRESHOLD
            
            vector_store = self.get_vector_store()
            results = vector_store.similarity_search_with_relevance_scores(
                query,
                k=k,
                score_threshold=threshold
            )
            
            # Format results consistently
            formatted_results = [
                {
                    'document': doc.page_content,
                    'score': score,
                    'metadata': doc.metadata
                }
                for doc, score in results
            ]
            
            logger.info(f"Found {len(formatted_results)} results above threshold {threshold}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            raise

    def create_vector_store(self, documents: List[Document], summaries: Optional[Dict[str, str]] = None):
        """Create a new vector store with batched processing"""
        try:
            if not documents:
                logger.warning("No documents provided to create vector store")
                return None

            # Reset the client to clear any existing collections
            self.chroma_client.reset()
            
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
            
            # Store document hashes in collection metadata using correct API
            collection = self.chroma_client.get_collection(self.COLLECTION_NAME)
            self._store_document_hashes(collection, self._get_document_hashes(documents))
            
            logger.info(f"Successfully created vector store with {len(documents)} documents")
            return vector_store
                
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            raise

    def get_or_create_vector_store(self, force_recreate: bool = False, summaries: Optional[Dict[str, str]] = None):
        """Get existing or create new vector store with incremental updates"""
        if not self.doc_processor:
            raise ValueError("Document processor not set")
            
        try:
            # Load new documents
            new_documents = self.doc_processor.load_documents()
            if not new_documents:
                raise ValueError("No documents loaded from document processor")
            
            # Calculate new document hashes
            new_doc_hashes = self._get_document_hashes(new_documents)
            
            # Always create fresh vector store when force_recreate is True
            if force_recreate:
                logger.info("Force recreating vector store")
                return self.create_vector_store(new_documents, summaries)
            
            try:
                # Try to get existing vector store
                vector_store = self.get_vector_store()
                existing_hashes = self._load_existing_hashes()
                
                # Find changed and new documents
                changed_docs = []
                unchanged_docs = []
                
                for doc in new_documents:
                    source = doc.metadata['source']
                    if source not in existing_hashes or existing_hashes[source] != new_doc_hashes[source]:
                        changed_docs.append(doc)
                    else:
                        unchanged_docs.append(doc)
                
                if changed_docs:
                    logger.info(f"Found {len(changed_docs)} new or modified documents")
                    # Process changed documents in batches
                    for i in range(0, len(changed_docs), self.BATCH_SIZE):
                        batch = changed_docs[i:i + self.BATCH_SIZE]
                        texts = [doc.page_content for doc in batch]
                        metadatas = [doc.metadata for doc in batch]
                        vector_store.add_texts(texts=texts, metadatas=metadatas)
                        
                        if i + self.BATCH_SIZE < len(changed_docs):
                            time.sleep(self.BATCH_DELAY)
                    
                    # Update hashes using correct API
                    collection = self.chroma_client.get_collection(self.COLLECTION_NAME)
                    self._store_document_hashes(collection, new_doc_hashes)
                    
                return vector_store
                
            except Exception as e:
                logger.warning(f"Error accessing existing vector store: {e}")
                logger.info("Creating new vector store")
                return self.create_vector_store(new_documents, summaries)
                
        except Exception as e:
            logger.error(f"Error in get_or_create_vector_store: {str(e)}")
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

    def shutdown(self):
        """Properly shutdown the vector store"""
        try:
            if hasattr(self, 'chroma_client'):
                self.chroma_client.reset()
                del self.chroma_client
            
            if hasattr(self, 'persist_directory') and self.persist_directory.exists():
                shutil.rmtree(str(self.persist_directory))
                self._temp_dirs.discard(self.persist_directory)
                logger.info("Vector store shutdown and temporary directory cleaned up")
        except Exception as e:
            logger.error(f"Error shutting down vector store: {e}")

    def cleanup_all(self):
        """Cleanup method called on system exit"""
        logger.info("Performing final cleanup...")
        try:
            self.shutdown()
            self.cleanup_temp_directories()
            logger.info("Final cleanup completed")
        except Exception as e:
            logger.error(f"Error during final cleanup: {e}")

    @classmethod
    def reset_instances(cls):
        """Reset all instances (useful for testing)"""
        for instance in cls._instances.values():
            try:
                instance.cleanup_all()
            except:
                pass
        cls._instances.clear()

    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            self.cleanup_all()
        except Exception as e:
            logger.error(f"Error during destructor cleanup: {e}")
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
import re
from typing import List
from langchain.text_splitter import TextSplitter
from langchain.schema import Document

class CustomMarkdownSplitter(TextSplitter):
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.markdown_header_pattern = re.compile(r'^#+\s+')

    def split_text(self, text: str) -> list[str]:
        if not text.strip():
            return []

        chunks = []
        lines = text.split('\n')
        current_chunk = []
        current_size = 0

        for line in lines:
            line_size = len(line) + 1  # +1 for newline
            is_header = bool(self.markdown_header_pattern.match(line))

            # Start new chunk if: header found, or current chunk would exceed size
            if (current_size + line_size > self.chunk_size and current_chunk) or is_header:
                if current_chunk:  # Only add non-empty chunks
                    chunk_text = '\n'.join(current_chunk).strip()
                    if chunk_text:  # Extra check to ensure no empty chunks
                        chunks.append(chunk_text)
                current_chunk = []
                current_size = 0

            current_chunk.append(line)
            current_size += line_size

        # Add the last chunk if it exists
        if current_chunk:
            chunk_text = '\n'.join(current_chunk).strip()
            if chunk_text:
                chunks.append(chunk_text)

        return chunks

    def create_documents(self, texts: list[str], metadatas: list[dict] = None) -> List[Document]:
        """Create documents from a list of texts."""
        _metadatas = metadatas or [{}] * len(texts)
        return [
            Document(page_content=text, metadata=metadata)
            for text, metadata in zip(texts, _metadatas)
            if text.strip()  # Only create documents for non-empty texts
        ]

    def split_documents(self, documents: list[dict]) -> List[Document]:
        """Split documents."""
        texts = []
        metadatas = []
        for doc in documents:
            texts.extend(self.split_text(doc["page_content"]))
            metadatas.extend([doc["metadata"]] * len(self.split_text(doc["page_content"])))
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
from app.main import create_app
import logging

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

import logging
import sys
from pathlib import Path
from unittest.mock import Mock
import pytest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import required modules
from langchain_core.messages import HumanMessage, AIMessage
from app.core.qa_chain import QAChainManager
from app.config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL
from langchain_anthropic import ChatAnthropic
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores import Chroma

# Fixtures
@pytest.fixture
def llm():
    return ChatAnthropic(
        model=CLAUDE_MODEL,
        anthropic_api_key=ANTHROPIC_API_KEY,
        temperature=0
    )

@pytest.fixture
def qa_manager():
    return QAChainManager()

@pytest.fixture
def mock_vector_store():
    mock_store = Mock(spec=Chroma)
    mock_store.as_retriever.return_value = Mock()
    
    # Mock document for retriever
    mock_doc = Mock()
    mock_doc.page_content = "Sample T# documentation content"
    mock_doc.metadata = {"source": "test.md"}
    mock_store.as_retriever.return_value.get_relevant_documents.return_value = [mock_doc]
    return mock_store

# Tests
def test_chain_creation(qa_manager, mock_vector_store):
    """Test QA chain creation"""
    chain = qa_manager.create_qa_chain(mock_vector_store)
    assert isinstance(chain, ConversationalRetrievalChain)
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
    # Create the chain
    chain = qa_manager.create_qa_chain(mock_vector_store)
    
    # Test with a simple query
    result = qa_manager.process_query(chain, "How do I use variables in T#?")
    
    # Verify result structure
    assert 'answer' in result
    assert 'source_documents' in result
    assert 'chat_history' in result
    
    # Verify chat history is updated
    history = qa_manager.get_chat_history()
    assert len(history) > 0
    logger.info("Query processing test completed")

def test_error_handling(qa_manager, mock_vector_store):
    """Test error handling in query processing"""
    chain = qa_manager.create_qa_chain(mock_vector_store)
    
    # Test with empty query
    result = qa_manager.process_query(chain, "")
    assert result['answer'] == "Please provide a valid question."
    
    # Test with None query
    result = qa_manager.process_query(chain, None)
    assert 'error' in result['answer'].lower()
    logger.info("Error handling test completed")

def test_memory_persistence(qa_manager, mock_vector_store):
    """Test chat memory persistence across queries"""
    chain = qa_manager.create_qa_chain(mock_vector_store)
    
    # Process multiple queries
    queries = [
        "What is T#?",
        "How do I declare variables?",
        "Can you show an example?"
    ]
    
    for query in queries:
        result = qa_manager.process_query(chain, query)
    
    # Verify memory contains all interactions
    history = qa_manager.get_chat_history()
    assert len(history) == len(queries) * 2  # Each query should have a response
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
