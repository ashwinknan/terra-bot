# app/core/vector_store.py

import logging
import shutil
import tempfile
import time
from pathlib import Path
from typing import List, Dict, Optional, Union
import atexit
import numpy as np
import chromadb

from langchain_cohere import CohereEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

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

logger = logging.getLogger(__name__)

class VectorStoreManager:
    _instances = {}
    _temp_dirs = set()
    COLLECTION_NAME = "game_development_docs"
    BATCH_DELAY = 2
    BATCH_SIZE = 5  # Reduced from 50
    EMBEDDING_DELAY = 0.5  # Reduced from 2

    @classmethod
    def reset_instances(cls):
        """Reset all instances and clean up temporary directories"""
        for instance in cls._instances.values():
            try:
                instance.cleanup_all()
            except:
                pass
        cls._instances.clear()
        cls._temp_dirs.clear()
    
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
            
            # Initialize embeddings with simplified configuration for Cohere
            self.embeddings = CohereEmbeddings(
                cohere_api_key=COHERE_API_KEY,
                model=EMBEDDING_MODEL
            )
            
            # Initialize ChromaDB client with unified settings
            try:
                from chromadb.config import Settings
                
                self.chroma_settings = Settings(
                    persist_directory=str(self.persist_directory),
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True
                )
                
                self.chroma_client = chromadb.Client(self.chroma_settings)
                
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB client: {str(e)}")
                self.chroma_client = chromadb.PersistentClient(
                    path=str(self.persist_directory)
                )
            
            logger.info("Vector store initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise

    def _process_text_for_embedding(self, text: Union[str, List[str]]) -> List[str]:
        """Process text before embedding to ensure correct format"""
        def normalize_text(t: str) -> str:
            # Convert to string and normalize whitespace
            return ' '.join(str(t).split())
            
        if isinstance(text, str):
            return [normalize_text(text)]
            
        if not isinstance(text, list):
            return [normalize_text(str(text))]
            
        # Process list of texts
        return [normalize_text(t) for t in text]

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
                    embedding_function=self.embeddings,
                    persist_directory=str(self.persist_directory)
                )
                
                # Process new documents in batches
                new_docs = []
                try:
                    collection = self.chroma_client.get_collection(self.COLLECTION_NAME)
                    if collection:
                        existing_ids = set(collection.get()['ids'])
                        for doc in documents:
                            doc_id = f"{doc.metadata['source']}_{hash(doc.page_content)}"
                            if doc_id not in existing_ids:
                                new_docs.append(doc)
                except:
                    # If collection doesn't exist, add all documents
                    new_docs = documents
                
                if new_docs:
                    logger.info(f"Found {len(new_docs)} new documents to add")
                    for i in range(0, len(new_docs), self.BATCH_SIZE):
                        batch = new_docs[i:i + self.BATCH_SIZE]
                        
                        # Process texts before adding
                        texts = [doc.page_content for doc in batch]
                        texts = self._process_text_for_embedding(texts)
                        
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
            raise

    def create_vector_store(self, documents: List[Document]) -> Chroma:
        """Create a new vector store with optimized batched processing"""
        try:
            if not documents:
                logger.warning("No documents provided to create vector store")
                raise ValueError("Cannot create vector store with empty document list")

            # Reset the client
            self.chroma_client.reset()
            
            logger.info(f"Creating new vector store with {len(documents)} documents")
            
            # Create new Chroma vector store with initial small batch
            first_batch = documents[:self.BATCH_SIZE]
            texts = [doc.page_content for doc in first_batch]
            texts = self._process_text_for_embedding(texts)
            metadatas = [doc.metadata for doc in first_batch]
            
            vector_store = Chroma.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas,
                client=self.chroma_client,
                collection_name=self.COLLECTION_NAME
            )

            # Process remaining documents in smaller batches
            remaining_docs = documents[self.BATCH_SIZE:]
            for i in range(0, len(remaining_docs), self.BATCH_SIZE):
                batch = remaining_docs[i:i + self.BATCH_SIZE]
                texts = [doc.page_content for doc in batch]
                texts = self._process_text_for_embedding(texts)
                metadatas = [doc.metadata for doc in batch]
                
                try:
                    vector_store.add_texts(texts=texts, metadatas=metadatas)
                    if i + self.BATCH_SIZE < len(remaining_docs):
                        time.sleep(self.EMBEDDING_DELAY)
                except Exception as e:
                    logger.error(f"Error processing batch {i//self.BATCH_SIZE}: {str(e)}")
                    continue
            
            logger.info(f"Successfully created vector store with {len(documents)} documents")
            return vector_store
                    
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            raise

    def similarity_search_with_filter(self, query: str, filter_dict: Dict, k: int = 4,fetch_k: Optional[int] = None) -> List[Document]:
        """Perform similarity search with metadata filtering"""
        try:
            collection = self.chroma_client.get_collection(name=self.COLLECTION_NAME)
            
            # Process query text - ensure it's a string
            if not isinstance(query, str):
                query = str(query)
            
            # For MMR, fetch more candidates
            if fetch_k is None:
                fetch_k = k * 2
            
            # Convert filter dict to Chroma filter format
            where = {f"metadata.{key}": value for key, value in filter_dict.items()}
            
            results = collection.query(
                query_texts=[query],  # Pass as list
                n_results=k,
                where=where,
                include=["documents", "metadatas"]
            )
            
            # Convert results to Document objects
            documents = []
            if results and results['documents'] and results['documents'][0]:
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
        try:
            logger = logging.getLogger(__name__)
            handler = logging.StreamHandler()
            logger.addHandler(handler)
            
            try:
                logger.info("Performing final cleanup...")
                
                # First cleanup vector store
                if hasattr(self, 'vector_store'):
                    try:
                        self.vector_store.delete_collection()
                    except:
                        pass
                        
                # Then cleanup embeddings
                if hasattr(self, 'embeddings'):
                    try:
                        # Ensure any embedding background tasks are completed
                        if hasattr(self.embeddings, '_executor'):
                            self.embeddings._executor.shutdown(wait=True)
                    except:
                        pass
                        
                # Finally cleanup temporary directories
                try:
                    self.cleanup_temp_directories()
                except:
                    pass

                if hasattr(self, 'chroma_client'):
                    try:
                        self.chroma_client.reset()
                    except:
                        pass
                        
                logger.info("Final cleanup completed")
                
            finally:
                # Always remove and close the handler
                handler.close()
                logger.removeHandler(handler)
                
        except Exception:
            # Don't log here since logger might be closed
            pass

    def cleanup_temp_directories(self):
        """Clean up any temporary ChromaDB directories"""
        try:
            temp_dir = Path(tempfile.gettempdir())
            
            # Clean up tracked directories
            for temp_path in self._temp_dirs.copy():
                if temp_path.exists():
                    try:
                        shutil.rmtree(str(temp_path))
                        self._temp_dirs.remove(temp_path)
                    except Exception as e:
                        pass
            
            # Clean up untracked directories
            for item in temp_dir.glob("tmp*"):
                if item.is_dir():
                    try:
                        if any(f.name == 'chroma.sqlite3' for f in item.glob('*')) or \
                           any(f.name == 'index' for f in item.glob('*')):
                            shutil.rmtree(str(item))
                    except:
                        pass
                        
        except Exception:
            pass

    @classmethod
    def reset_instances(cls):
        """Reset all instances and clean up temporary directories"""
        for instance in cls._instances.values():
            try:
                instance.cleanup_all()
            except:
                pass
        cls._instances.clear()
        cls._temp_dirs.clear()