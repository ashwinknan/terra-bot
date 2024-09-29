import re
from langchain.text_splitter import TextSplitter

class CustomMarkdownSplitter(TextSplitter):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.markdown_header_pattern = re.compile(r'^#+\s+')
        self.code_block_pattern = re.compile(r'```[\s\S]*?```')

    def split_text(self, text: str) -> list[str]:
        chunks = []
        current_chunk = ""
        current_chunk_size = 0

        lines = text.split('\n')
        in_code_block = False

        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block

            is_header = self.markdown_header_pattern.match(line)
            
            if (current_chunk_size + len(line) > self.chunk_size and current_chunk) or is_header:
                chunks.append(current_chunk.strip())
                current_chunk = ""
                current_chunk_size = 0

            current_chunk += line + '\n'
            current_chunk_size += len(line) + 1

            if in_code_block and current_chunk_size > self.chunk_size:
                chunks.append(current_chunk.strip())
                current_chunk = ""
                current_chunk_size = 0

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def create_documents(self, texts: list[str], metadatas: list[dict] = None) -> list[dict]:
        """Create documents from a list of texts."""
        _metadatas = metadatas or [{}] * len(texts)
        documents = [{"page_content": text, "metadata": metadata} for text, metadata in zip(texts, _metadatas)]
        return documents

    def split_documents(self, documents: list[dict]) -> list[dict]:
        """Split documents."""
        texts = []
        metadatas = []
        for doc in documents:
            texts.extend(self.split_text(doc["page_content"]))
            metadatas.extend([doc["metadata"]] * len(self.split_text(doc["page_content"])))
        return self.create_documents(texts, metadatas)