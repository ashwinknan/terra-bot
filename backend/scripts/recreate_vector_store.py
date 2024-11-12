import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import logging
from app.main import create_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def recreate_vector_store():
    """Utility script to recreate the vector store"""
    logger.info("Recreating vector store...")
    try:
        app = create_app(force_recreate=True)
        with app.app_context():
            logger.info("Vector store recreation completed successfully")
    except Exception as e:
        logger.error(f"Failed to recreate vector store: {str(e)}")
        raise

if __name__ == "__main__":
    recreate_vector_store()