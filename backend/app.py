import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import argparse
from src.vector_store import get_or_create_vector_store
from src.qa_chain import create_qa_chain

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize vector store and QA chain
vector_store = None
qa_chain = None

def initialize_app(force_recreate=False):
    global vector_store, qa_chain
    vector_store = get_or_create_vector_store(force_recreate=force_recreate)
    qa_chain = create_qa_chain(vector_store)
    logger.info("Application initialized successfully.")

# Call initialize_app right after creating the Flask app instance
initialize_app()

@app.route('/ask', methods=['POST', 'OPTIONS'])
def ask_question():
    if request.method == 'OPTIONS':
        return handle_options_request()
    
    data = request.json
    question = data.get('question', '')
    logger.info(f"Received question: {question}")
    
    try:
        logger.info(f"qa_chain type: {type(qa_chain)}")
        logger.info(f"vector_store type: {type(vector_store)}")
        
        if qa_chain is None:
            raise ValueError("qa_chain is not initialized")
        
        # Use the QA chain to get the answer
        result = qa_chain({"question": question})
        
        answer = result['answer']
        sources = [doc.metadata.get('source', 'Unknown') for doc in result.get('source_documents', [])]
        logger.info(f"Generated answer: {answer}")
        logger.info(f"Sources: {sources}")
        
        return jsonify({"answer": answer, "sources": sources})
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while processing your question."}), 500

def handle_options_request():
    response = jsonify({'message': 'OK'})
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST')
    return response

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the QA system')
    parser.add_argument('--recreate-vector-store', action='store_true', help='Force recreation of the vector store')
    args = parser.parse_args()

    initialize_app(force_recreate=args.recreate_vector_store)
    app.run(debug=True, host='0.0.0.0', port=5001)