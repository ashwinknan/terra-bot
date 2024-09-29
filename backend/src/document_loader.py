import os
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.schema import Document
from .text_splitter import CustomMarkdownSplitter
from utils.metadata_extractor import extract_metadata

def load_documents():
    documents = []
    custom_splitter = CustomMarkdownSplitter(chunk_size=1000, chunk_overlap=200)
    
    knowledge_base_path = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base')
    
    for filename in os.listdir(knowledge_base_path):
        filepath = os.path.join(knowledge_base_path, filename)
        if filename.endswith('.pdf'):
            loader = PyPDFLoader(filepath)
            docs = loader.load()
            # Ensure metadata values are strings, ints, or floats
            for doc in docs:
                doc.metadata = {k: str(v) if isinstance(v, bool) else v for k, v in doc.metadata.items()}
        elif filename.endswith('.md'):
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            metadata = extract_metadata(content, filename)
            chunks = custom_splitter.split_text(content)
            docs = [Document(page_content=chunk, metadata=metadata) for chunk in chunks]
        else:
            continue
        documents.extend(docs)
    return documents