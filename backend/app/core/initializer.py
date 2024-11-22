# File: backend/app/core/initializer.py

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
    MAX_RETRIES,
    RETRY_DELAY,
    MIN_CHUNK_SIZE,
    MAX_CHUNK_SIZE,
    CACHE_DIR
)

logger = logging.getLogger(__name__)

class AppComponents:
    """Singleton to store application components"""
    doc_processor = None
    vector_store_manager = None
    vector_store = None
    qa_chain_manager = None
    qa_chain = None

def _retry_with_backoff(func: Callable[[], Any], max_retries: int = MAX_RETRIES, initial_delay: float = RETRY_DELAY) -> Any:
    """Helper function to retry operations with exponential backoff"""
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
    """Initialize all application components"""
    try:
        logger.info("Starting application initialization...")
        
        # Setup paths
        base_path = Path(__file__).parent.parent.parent
        knowledge_base_path = base_path / "data" / "knowledge_base"
        
        # Ensure directory exists
        knowledge_base_path.mkdir(exist_ok=True, parents=True)
        
        # Initialize document processor with settings from config
        logger.info("Initializing document processor...")
        AppComponents.doc_processor = DocumentProcessor(
            knowledge_base_path=str(knowledge_base_path),
            max_retries=MAX_RETRIES,
            retry_delay=RETRY_DELAY,
            min_chunk_size=MIN_CHUNK_SIZE,
            max_chunk_size=MAX_CHUNK_SIZE
        )
        
        # Load documents
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
    """Safely shutdown all application components"""
    logger.info("Shutting down application...")
    try:
        if AppComponents.vector_store_manager:
            AppComponents.vector_store_manager.cleanup_all()
        if AppComponents.qa_chain_manager:
            AppComponents.qa_chain_manager.clear_memory()
        logger.info("Application shutdown completed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")