from flask import Blueprint, request, jsonify
import logging
from app.core.initializer import AppComponents
from app.config.settings import ALLOWED_ORIGIN
import re

logger = logging.getLogger(__name__)

# Create blueprint with unique name
api_bp = Blueprint('api', __name__, url_prefix='/api')

def is_valid_question(question: str) -> bool:
    """Validate question content"""
    # Check if question has actual words (not just special characters or numbers)
    if not re.search(r'[a-zA-Z]+', question):
        return False
    # Check if question is not too long (prevent abuse)
    if len(question) > 1000:
        return False
    return True

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
    logger.info(f"Received request: {request.method} {request.path}")
    logger.info(f"Request headers: {request.headers}")
    try:
        # Check if request has JSON content type
        if not request.is_json:
            return jsonify({"error": "No JSON data provided"}), 400
            
        try:
            data = request.get_json()
        except Exception:
            return jsonify({"error": "No JSON data provided"}), 400
            
        if not data or not isinstance(data, dict):
            return jsonify({"error": "No JSON data provided"}), 400
            
        if 'question' not in data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        question = data.get('question')
        
        # Type validation
        if not isinstance(question, str):
            return jsonify({"error": "Question must be a string"}), 422
            
        # Content validation
        question = question.strip()
        if not question:
            return jsonify({"error": "Question cannot be empty"}), 400
            
        # Validate question content
        if not is_valid_question(question):
            return jsonify({"error": "Invalid question format"}), 422
            
        logger.info(f"Received question: {question}")
        
        if not AppComponents.qa_chain or not AppComponents.qa_chain_manager:
            logger.error("QA chain is not initialized")
            return jsonify({
                "error": "Service not ready. Please try again later.",
                "status": "error"
            }), 503
        
        result = AppComponents.qa_chain_manager.process_query(
            AppComponents.qa_chain, 
            question
        )
        
        response = {
            "answer": result.get("answer", "No answer generated"),
            "sources": result.get("sources", []),
            "status": "success"
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", exc_info=True)
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

"""@api_bp.route('/ask', methods=['OPTIONS'])
def handle_ask_options():
    "Handle CORS preflight for ask endpoint"
    response = jsonify({'message': 'OK'})
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Origin'] = ALLOWED_ORIGIN
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response
"""
@api_bp.route('/', methods=['GET', 'HEAD'])
def root():
    """Handle root path requests"""
    return jsonify({
        "status": "online",
        "message": "RAG Game Assistant API is running. Use /api/ endpoints to interact."
    })