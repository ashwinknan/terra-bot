from src.vector_store import get_or_create_vector_store

def check_vector_store():
    vector_store = get_or_create_vector_store()
    print(f"Number of documents in vector store: {vector_store._collection.count()}")
    
    # Test queries
    test_queries = ["What is a logic template?", "What is a game object", "Can we use generics in T#"]
    for query in test_queries:
        results = vector_store.similarity_search(query, k=1)
        print(f"\nQuery: {query}")
        if results:
            print(f"Sample document content: {results[0].page_content[:200]}...")
            print(f"Source: {results[0].metadata.get('source', 'Unknown')}")
        else:
            print("No results found for this query.")

if __name__ == "__main__":
    check_vector_store()