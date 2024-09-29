from src.document_loader import load_documents

def check_document_loading():
    documents = load_documents()
    print(f"Number of documents loaded: {len(documents)}")
    if documents:
        print("\nSample documents:")
        for i, doc in enumerate(documents[:3]):  # Print details of first 3 documents
            print(f"\nDocument {i+1}:")
            print(f"Content preview: {doc.page_content[:200]}...")
            print(f"Metadata: {doc.metadata}")
    else:
        print("No documents were loaded.")

if __name__ == "__main__":
    check_document_loading()