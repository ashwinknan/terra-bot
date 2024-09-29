from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from config import OPENAI_API_KEY
from .document_loader import load_documents
import os
import shutil
from openai.error import OpenAIError

def create_vector_store(documents):
    try:
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        vector_store = Chroma.from_documents(
            documents,
            embeddings,
            collection_name="game_development_docs",
            persist_directory="./chroma_db"
        )
        return vector_store
    except OpenAIError as e:
        print(f"OpenAI API error occurred: {str(e)}")
        raise

def get_or_create_vector_store(force_recreate=False):
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    persist_directory = "./chroma_db"
    
    if force_recreate and os.path.exists(persist_directory):
        print(f"Forcing recreation of vector store. Removing existing directory: {persist_directory}")
        shutil.rmtree(persist_directory)
    
    if not os.path.exists(persist_directory):
        print(f"Vector store directory '{persist_directory}' does not exist. Creating new vector store.")
        documents = load_documents()
        return create_vector_store(documents)
    
    try:
        vector_store = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        print(f"Vector store loaded successfully.")
        if vector_store._collection.count() == 0:
            print("Vector store is empty. Recreating...")
            documents = load_documents()
            return create_vector_store(documents)
        return vector_store
    except Exception as e:
        print(f"Error loading vector store: {str(e)}")
        print("Creating new vector store.")
        documents = load_documents()
        return create_vector_store(documents)