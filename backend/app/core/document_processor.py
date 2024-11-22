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
        try:
            content_length = len(document.page_content)
            
            if not document.page_content.strip():
                raise ValueError("Empty chunk")
                
            if content_length < int(self.min_chunk_size):
                raise ValueError(f"Chunk too small ({content_length} chars)")
                
            if content_length > int(self.max_chunk_size):
                raise ValueError(f"Chunk too large ({content_length} chars)")
                
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