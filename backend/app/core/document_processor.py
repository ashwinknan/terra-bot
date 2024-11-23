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
from app.config.settings import (
    CHUNK_SIZE, 
    CHUNK_OVERLAP,
    MAX_RETRIES,
    RETRY_DELAY,
    MIN_CHUNK_SIZE,
    MAX_CHUNK_SIZE,
    CODE_CHUNK_SIZE,
    CODE_CHUNK_OVERLAP,
    MIN_CODE_CHUNK_SIZE,
    MAX_CODE_CHUNK_SIZE
)

logger = logging.getLogger(__name__)

class ProcessingError(Exception):
    """Custom exception for document processing errors"""
    pass

class DocType(Enum):
    RULESET = "ruleset"
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
                 max_retries: int = MAX_RETRIES,
                 retry_delay: float = RETRY_DELAY,
                 min_chunk_size: int = MIN_CHUNK_SIZE,
                 max_chunk_size: int = MAX_CHUNK_SIZE):
        """Initialize document processor with configuration"""
        self.knowledge_base_path = Path(knowledge_base_path)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self._reset_stats()
        self.custom_splitter = CustomMarkdownSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        logger.info(f"Initialized DocumentProcessor with path: {knowledge_base_path}")
        logger.info(f"Configuration: min_size={min_chunk_size}, max_size={max_chunk_size}")

    def _reset_stats(self):
        """Initialize/reset processing statistics"""
        self.processing_stats = {
            "total_files": 0,
            "successful_files": 0,
            "failed_files": 0,
            "total_chunks": 0,
            "retry_count": 0,
            "rejected_chunks": 0,
            "rejection_reasons": []
        }

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
            logger.debug(f"Document title: {title}")
            logger.debug(f"Content length: {len(content)} chars")

            # Split content into chunks with type-specific settings
            if doc_type == DocType.RULESET:
                logger.debug("Using ruleset settings for chunking")
                chunk_size = CHUNK_SIZE
                chunk_overlap = CHUNK_OVERLAP
            elif doc_type == DocType.FUNCTIONS:
                logger.debug("Using functions settings for chunking")
                chunk_size = CODE_CHUNK_SIZE
                chunk_overlap = CODE_CHUNK_OVERLAP
            else:  # EXAMPLE type
                logger.debug("Using example settings for chunking")
                chunk_size = CODE_CHUNK_SIZE
                chunk_overlap = CODE_CHUNK_OVERLAP
            
            logger.debug(f"Chunking with size={chunk_size}, overlap={chunk_overlap}")
            
            splitter = CustomMarkdownSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            
            chunks = splitter.split_text(content)
            logger.info(f"Split document into {len(chunks)} chunks")

            # Create documents with metadata
            documents = []
            for i, chunk in enumerate(chunks):
                if chunk.strip():  # Skip empty chunks
                    has_code = bool(re.search(r'```', chunk))
                    logger.debug(f"Processing chunk {i+1}/{len(chunks)}, has_code={has_code}")
                    
                    # Use different size limits based on content type
                    min_size = MIN_CODE_CHUNK_SIZE if has_code else MIN_CHUNK_SIZE
                    max_size = MAX_CODE_CHUNK_SIZE if has_code else MAX_CHUNK_SIZE
                    
                    # Validate chunk size
                    chunk_length = len(chunk)
                    if chunk_length < min_size or chunk_length > max_size:
                        logger.warning(
                            f"Chunk size {chunk_length} outside limits "
                            f"({min_size}, {max_size}) for {file_name}"
                        )
                        continue
                    
                    metadata = {
                        "source": file_name,
                        "doc_type": doc_type.value,
                        "title": title,
                        "has_code": has_code,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "processing_attempts": 0,
                        "chunk_size": chunk_length  # Added for debugging
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
        self._reset_stats()  # Reset stats at start of loading
        
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
        """Validate a document chunk with detailed logging"""
        try:
            content_length = len(document.page_content)
            has_code = document.metadata.get('has_code', False)
            
            logger.debug(f"Validating chunk: length={content_length}, has_code={has_code}")
            logger.debug(f"First 100 chars: {document.page_content[:100]}...")
            
            if not document.page_content.strip():
                reason = "Empty chunk"
                logger.warning(reason)
                self.processing_stats["rejection_reasons"].append(reason)
                self.processing_stats["rejected_chunks"] += 1
                return False
            
            # Use appropriate size limits based on content type
            min_size = MIN_CODE_CHUNK_SIZE if has_code else MIN_CHUNK_SIZE
            max_size = MAX_CODE_CHUNK_SIZE if has_code else MAX_CHUNK_SIZE
                
            if content_length < min_size:
                reason = f"Chunk too small ({content_length} chars < {min_size})"
                logger.warning(reason)
                self.processing_stats["rejection_reasons"].append(reason)
                self.processing_stats["rejected_chunks"] += 1
                return False
                
            if content_length > max_size:
                reason = f"Chunk too large ({content_length} chars > {max_size})"
                logger.warning(reason)
                self.processing_stats["rejection_reasons"].append(reason)
                self.processing_stats["rejected_chunks"] += 1
                return False
                
            logger.debug(f"Chunk validation successful: {content_length} chars")
            return True
            
        except Exception as e:
            logger.error(f"Chunk validation error: {str(e)}")
            return False

    def _log_processing_summary(self, failed_files: List[Tuple[str, List[str]]]):
        """Log detailed processing summary"""
        logger.info("\n=== Document Processing Summary ===")
        logger.info(f"Total files processed: {self.processing_stats['total_files']}")
        logger.info(f"Successfully processed: {self.processing_stats['successful_files']}")
        logger.info(f"Failed to process: {self.processing_stats['failed_files']}")
        logger.info(f"Total chunks created: {self.processing_stats['total_chunks']}")
        logger.info(f"Total retry attempts: {self.processing_stats['retry_count']}")
        logger.info(f"Rejected chunks: {self.processing_stats['rejected_chunks']}")
        
        if self.processing_stats['rejection_reasons']:
            logger.info("\nRejection Reasons:")
            for reason in self.processing_stats['rejection_reasons']:
                logger.info(f"  - {reason}")
        
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