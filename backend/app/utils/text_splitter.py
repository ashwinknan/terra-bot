# app/utils/text_splitter.py

import re
from typing import List
from langchain.text_splitter import TextSplitter
from langchain.schema import Document
from app.config.settings import (
    CHUNK_SIZE, 
    CHUNK_OVERLAP, 
    MIN_CHUNK_SIZE, 
    MAX_CHUNK_SIZE,
    CODE_CHUNK_SIZE,
    CODE_CHUNK_OVERLAP,
    MAX_CODE_CHUNK_SIZE
)

class CustomMarkdownSplitter(TextSplitter):
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        super().__init__()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = MIN_CHUNK_SIZE
        self.max_chunk_size = MAX_CHUNK_SIZE

        self.markdown_header_pattern = re.compile(r'^#+\s+')
        self.code_block_pattern = re.compile(r'```[\s\S]*?```')
        self.class_pattern = re.compile(r'public class (\w+)')
        self.method_pattern = re.compile(r'\s+(private|public|protected)\s+\w+\s+\w+\s*\([^)]*\)\s*\{')
        self.control_pattern = re.compile(r'^\s*(if|for|while|foreach|switch)\s*\(')

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
        """Split code blocks by logical boundaries with improved size handling"""
        # Remove code fence markers
        code = text.replace('```csharp\n', '').replace('```', '')
        
        # Skip empty or too small code blocks
        if len(code.strip()) < self.min_chunk_size:
            return []
        
        # For very large code blocks, split by logical boundaries
        chunks = []
        current_chunk = []
        current_size = 0
        in_method = False
        method_lines = []
        
        lines = code.split('\n')
        buffer = []  # Add a buffer to accumulate small chunks
        buffer_size = 0
        
        for line in lines:
            line_size = len(line) + 1
            
            # Method start detection
            if self.method_pattern.search(line):
                # Handle any buffered content first
                if buffer:
                    if buffer_size >= self.min_chunk_size:
                        chunks.append(f"```csharp\n{chr(10).join(buffer)}\n```")
                    buffer = []
                    buffer_size = 0
                    
                # Save previous method if exists
                if method_lines and current_size > self.min_chunk_size:
                    chunk_content = '\n'.join(method_lines)
                    chunks.append(f"```csharp\n{chunk_content}\n```")
                    method_lines = []
                    current_size = 0
                    
                in_method = True
                method_lines = [line]
                current_size = line_size
                continue
                
            if in_method:
                # If adding this line would exceed max size, split the method
                if current_size + line_size > MAX_CODE_CHUNK_SIZE - 20:  # Leave room for fence markers
                    if method_lines:
                        chunk_content = '\n'.join(method_lines)
                        chunks.append(f"```csharp\n{chunk_content}\n```")
                        method_lines = [line]
                        current_size = line_size
                        in_method = line.strip() != '}'
                else:
                    method_lines.append(line)
                    current_size += line_size
                    
                    # Method end detection
                    if line.strip() == '}':
                        if current_size >= self.min_chunk_size:
                            chunk_content = '\n'.join(method_lines)
                            chunks.append(f"```csharp\n{chunk_content}\n```")
                        method_lines = []
                        current_size = 0
                        in_method = False
                continue
            
            # Handle non-method code
            if self.class_pattern.search(line) or buffer_size + line_size > MAX_CODE_CHUNK_SIZE - 20:
                if buffer and buffer_size >= self.min_chunk_size:
                    chunks.append(f"```csharp\n{chr(10).join(buffer)}\n```")
                buffer = []
                buffer_size = 0
            
            buffer.append(line)
            buffer_size += line_size
            
            # Force split if we're approaching the limit
            if buffer_size >= MAX_CODE_CHUNK_SIZE - 100:  # Add some buffer
                if buffer_size >= self.min_chunk_size:
                    chunks.append(f"```csharp\n{chr(10).join(buffer)}\n```")
                buffer = []
                buffer_size = 0
        
        # Handle remaining content
        if method_lines and current_size >= self.min_chunk_size:
            chunk_content = '\n'.join(method_lines)
            chunks.append(f"```csharp\n{chunk_content}\n```")
        elif buffer and buffer_size >= self.min_chunk_size:
            chunks.append(f"```csharp\n{chr(10).join(buffer)}\n```")
        
        return [chunk for chunk in chunks if len(chunk.strip()) >= self.min_chunk_size]

    def _split_method_chunk(self, content: str) -> List[str]:
        """Split a large method into smaller logical chunks"""
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        brace_count = 0
        
        for line in lines:
            line_size = len(line) + 1
            line_stripped = line.strip()
            
            # Track brace depth
            brace_count += line_stripped.count('{') - line_stripped.count('}')
            
            # Determine if this is a good split point
            is_split_point = (
                brace_count == 0 and  # At same brace level
                (line_stripped == '' or  # Empty line
                 self.control_pattern.match(line) or  # Control structure
                 line_stripped.endswith(';'))  # Statement end
            )
            
            if current_size + line_size > self.max_chunk_size:
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size
                
                # Split at logical boundaries if chunk is large enough
                if is_split_point and current_size > self.min_chunk_size:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = []
                    current_size = 0
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
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