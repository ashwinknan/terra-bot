# app/utils/text_splitter.py

import re
from typing import List
from langchain.text_splitter import TextSplitter
from langchain.schema import Document
from app.config.settings import CHUNK_SIZE, CHUNK_OVERLAP, MIN_CHUNK_SIZE, MAX_CHUNK_SIZE

class CustomMarkdownSplitter(TextSplitter):
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        super().__init__()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = MIN_CHUNK_SIZE
        self.markdown_header_pattern = re.compile(r'^#+\s+')
        self.code_block_pattern = re.compile(r'```[\s\S]*?```')
        self.class_pattern = re.compile(r'public class (\w+)')
        self.method_pattern = re.compile(r'\s+(private|public|protected)\s+\w+\s+\w+\s*\([^)]*\)\s*\{')

    def split_text(self, text: str) -> List[str]:
        if not text.strip():
            return []

        # First split into markdown sections and code blocks
        sections = self._split_into_sections(text)
        
        # Process each section appropriately
        chunks = []
        for section_type, content in sections:
            if section_type == "markdown":
                chunks.extend(self._split_markdown(content))
            elif section_type == "code":
                chunks.extend(self._split_code_block(content))

        # Restore proper chunk sizes by combining small chunks
        final_chunks = self._combine_small_chunks(chunks)
        
        return final_chunks

    def _split_into_sections(self, text: str) -> List[tuple]:
        """Split text into alternating markdown and code sections"""
        sections = []
        last_end = 0
        
        for match in self.code_block_pattern.finditer(text):
            # Add markdown section before code block
            if match.start() > last_end:
                sections.append(("markdown", text[last_end:match.start()]))
            
            # Add code block
            sections.append(("code", match.group(0)))
            last_end = match.end()
        
        # Add remaining markdown section
        if last_end < len(text):
            sections.append(("markdown", text[last_end:]))
            
        return sections

    def _split_markdown(self, text: str) -> List[str]:
        """Split markdown content by headers"""
        chunks = []
        current_chunk = []
        current_size = 0
        
        lines = text.split('\n')
        
        for line in lines:
            line_size = len(line) + 1
            
            # Start new chunk on header or size limit
            if (self.markdown_header_pattern.match(line) or 
                current_size + line_size > self.chunk_size) and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            current_chunk.append(line)
            current_size += line_size
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks

    def _split_code_block(self, text: str) -> List[str]:
        """Split code blocks by logical boundaries"""
        # Remove code fence markers
        code = text.replace('```csharp\n', '').replace('```', '')
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        # Split into logical sections (classes, methods)
        lines = code.split('\n')
        
        for line in lines:
            line_size = len(line) + 1
            
            # Start new chunk on class or method definition, or size limit
            if ((self.class_pattern.search(line) or self.method_pattern.search(line)) and
                current_size > self.min_chunk_size) or current_size + line_size > MAX_CHUNK_SIZE:
                if current_chunk:
                    chunks.append('```csharp\n' + '\n'.join(current_chunk) + '\n```')
                current_chunk = []
                current_size = 0
            
            current_chunk.append(line)
            current_size += line_size
        
        if current_chunk:
            chunks.append('```csharp\n' + '\n'.join(current_chunk) + '\n```')
        
        return chunks

    def _combine_small_chunks(self, chunks: List[str]) -> List[str]:
        """Combine chunks that are too small"""
        combined_chunks = []
        current_chunk = []
        current_size = 0
        
        for chunk in chunks:
            chunk_size = len(chunk)
            
            if chunk_size > MAX_CHUNK_SIZE:
                # Split oversized chunk
                if current_chunk:
                    combined_chunks.append('\n'.join(current_chunk))
                    current_chunk = []
                    current_size = 0
                # Split the large chunk by size while preserving markdown/code structure
                split_chunks = self._split_oversized_chunk(chunk)
                combined_chunks.extend(split_chunks)
            elif current_size + chunk_size > MAX_CHUNK_SIZE:
                combined_chunks.append('\n'.join(current_chunk))
                current_chunk = [chunk]
                current_size = chunk_size
            else:
                current_chunk.append(chunk)
                current_size += chunk_size
                
                # Check if we've reached a good size
                if current_size >= self.min_chunk_size:
                    combined_chunks.append('\n'.join(current_chunk))
                    current_chunk = []
                    current_size = 0
        
        if current_chunk:
            # If remaining chunk is too small, append to previous
            if current_size < self.min_chunk_size and combined_chunks:
                last_chunk = combined_chunks.pop()
                combined_chunks.append(last_chunk + '\n' + '\n'.join(current_chunk))
            else:
                combined_chunks.append('\n'.join(current_chunk))
        
        return combined_chunks

    def _split_oversized_chunk(self, chunk: str) -> List[str]:
        """Split an oversized chunk while preserving structure"""
        # If it's a code block, split by methods
        if chunk.startswith('```') and chunk.endswith('```'):
            return self._split_code_block(chunk)
        
        # Otherwise split by size while trying to keep paragraphs together
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in chunk.split('\n'):
            line_size = len(line) + 1
            
            if current_size + line_size > MAX_CHUNK_SIZE:
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            current_chunk.append(line)
            current_size += line_size
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks

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