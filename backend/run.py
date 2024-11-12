import logging
import sys
from app.main import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

# Suppress unnecessary logging
logging.getLogger('chromadb').setLevel(logging.WARNING)
logging.getLogger('cohere').setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    try:
        logger.info("Starting application initialization...")
        app = create_app(force_recreate=True)
        
        logger.info("=== Initialization complete ===")
        logger.info("Starting Flask server on http://0.0.0.0:5001")
        
        # Start the Flask server
        app.run(
            host='0.0.0.0',
            port=5001,
            debug=False,  # Set to False initially to avoid double initialization
            use_reloader=False  # Disable reloader to avoid double initialization
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        sys.exit(1)