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