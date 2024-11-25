# File: backend/app/main.py

import logging
import argparse
import os
from flask import Flask, jsonify
from flask_cors import CORS
from app.api.routes import api_bp
from app.core.initializer import initialize_app
from app.utils.version_check import check_versions
from app.utils.llm_health_check import check_llm_connection
from app.config.settings import DEBUG, ALLOWED_ORIGIN

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app(force_recreate=False):
    """Application factory function"""
    try:
        app = Flask(__name__)
        
        # Configure CORS with settings from config
        CORS(app, 
            origins=[ALLOWED_ORIGIN],
            methods=["GET", "POST", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
            supports_credentials=True,
            expose_headers=["Content-Type"],
            max_age=3600
        )
        
        # Add CORS headers to all responses
        @app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            response.headers.add('Access-Control-Allow-Origin', ALLOWED_ORIGIN)
            return response
        
        # Initialize components before registering blueprints
        logger.info("Starting application initialization...")
        if not check_versions():
            logger.warning("Version mismatches detected")
        if not check_llm_connection():
            logger.error("LLM connection check failed")
            
        # Initialize app (blocking)
        initialize_app(force_recreate)
        logger.info("Application initialization completed")
        
        # Register blueprints
        app.register_blueprint(api_bp, url_prefix='/api')
        
        # Add basic route for root path
        @app.route('/')
        def root():
            return jsonify({
                "status": "healthy",
                "message": "RAG Game Assistant API"
            })
        
        logger.info("Application creation completed successfully")
        return app
        
    except Exception as e:
        logger.error(f"Error creating application: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Run the QA system')
    parser.add_argument('--recreate-vector-store', action='store_true', 
                      help='Force recreation of the vector store')
    args = parser.parse_args()

    app = create_app(force_recreate=args.recreate_vector_store)
    
    port = int(os.environ.get('PORT', 5001))
    logger.info(f"Starting Flask server on port {port}...")
    app.run(debug=DEBUG, host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()