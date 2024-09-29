from src.vector_store import get_or_create_vector_store
from openai.error import OpenAIError

def recreate_vector_store():
    print("Recreating vector store...")
    try:
        vector_store = get_or_create_vector_store(force_recreate=True)
        doc_count = vector_store._collection.count()
        print(f"Vector store recreated. Number of documents: {doc_count}")
        if doc_count == 0:
            print("WARNING: Vector store is empty. Check your OpenAI API quota and try again.")
    except OpenAIError as e:
        print(f"Failed to recreate vector store due to OpenAI API error: {str(e)}")
        print("Please check your API quota and try again later.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    recreate_vector_store()