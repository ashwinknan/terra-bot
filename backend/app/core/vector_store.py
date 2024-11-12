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