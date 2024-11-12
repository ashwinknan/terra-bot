# app/main.py
import logging
import argparse
from flask import Flask
from flask_cors import CORS
from app.api.routes import api_bp
from app.core.initializer import initialize_app
from app.utils.version_check import check_versions
from app.utils.llm_test import test_llm
from app.config.settings import DEBUG, ALLOWED_ORIGIN

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app(force_recreate=False):
    """Application factory function"""
    # Check versions before starting
    if not check_versions():
        logger.warning("Version mismatches detected. Application may not work as expected.")

    # Test LLM
    if not test_llm():
        logger.error("LLM test failed - check your configuration")
        raise RuntimeError("LLM test failed")
    
    logger.info("Creating Flask application...")
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, origins=[ALLOWED_ORIGIN])
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Initialize components
    logger.info("Initializing application components...")
    initialize_app(force_recreate)
    
    logger.info("Application creation completed successfully")
    return app

def main():
    parser = argparse.ArgumentParser(description='Run the QA system')
    parser.add_argument('--recreate-vector-store', action='store_true', 
                      help='Force recreation of the vector store')
    args = parser.parse_args()

    app = create_app(force_recreate=args.recreate_vector_store)
    logger.info("Starting Flask server...")
    app.run(debug=DEBUG, host='0.0.0.0', port=5001)

if __name__ == '__main__':
    main()