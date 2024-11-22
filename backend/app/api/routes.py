# app/api/routes.py

from flask import Blueprint, request, jsonify
import logging
from app.core.initializer import AppComponents

logger = logging.getLogger(__name__)

# Create blueprint with unique name
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        components_status = {
            "doc_processor": AppComponents.doc_processor is not None,
            "vector_store": AppComponents.vector_store is not None,
            "qa_chain": AppComponents.qa_chain is not None
        }
        
        vector_store_count = 0
        if AppComponents.vector_store:
            try:
                collection = AppComponents.vector_store._collection
                vector_store_count = collection.count()
            except Exception as e:
                logger.error(f"Error getting vector store count: {str(e)}")
        
        return jsonify({
            "status": "healthy",
            "components": components_status,
            "vector_store_documents": vector_store_count,
            "message": "RAG Chatbot API is running"
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@api_bp.route('/ask', methods=['POST'])
def ask_question():
    """Handle question answering"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        question = data.get('question', '').strip()
        if not question:
            return jsonify({"error": "Question cannot be empty"}), 400
            
        logger.info(f"Received question: {question}")
        
        if AppComponents.qa_chain is None:
            logger.error("QA chain is not initialized")
            return jsonify({"error": "Service not ready. Please try again later."}), 503
        
        result = AppComponents.qa_chain_manager.process_query(AppComponents.qa_chain, question)
        
        # Add logging for debugging
        logger.info(f"QA Chain result: {result}")
        
        response = {
            "answer": result.get("answer", "No answer generated"),
            "sources": [doc.metadata.get('source', 'Unknown') for doc in result.get('source_documents', [])],
        }
        
        logger.info(f"Generated answer: {response['answer']}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", exc_info=True)
        return jsonify({
            "error": str(e),
            "answer": "An error occurred while processing your question.",
        }), 500

@api_bp.route('/ask', methods=['OPTIONS'])
def handle_ask_options():
    """Handle CORS preflight for ask endpoint"""
    response = jsonify({'message': 'OK'})
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST')
    return response