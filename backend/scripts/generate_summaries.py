import logging
import sys
from pathlib import Path

# Add the project root to Python path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from app.core.document_processor import DocumentProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_summaries():
    """Generate and save document summaries"""
    try:
        # Setup paths
        base_path = Path(__file__).parent.parent
        knowledge_base_path = base_path / "data" / "knowledge_base"
        summaries_path = base_path / "data" / "summaries"
        
        # Ensure directories exist
        knowledge_base_path.mkdir(exist_ok=True, parents=True)
        summaries_path.mkdir(exist_ok=True, parents=True)
        
        logger.info("Initializing document processor...")
        doc_processor = DocumentProcessor(
            knowledge_base_path=str(knowledge_base_path),
            summaries_path=str(summaries_path)
        )
        
        logger.info("Generating summaries...")
        summaries = doc_processor.generate_summaries()
        logger.info(f"Successfully generated {len(summaries)} summaries")
        
    except Exception as e:
        logger.error(f"Error generating summaries: {str(e)}")
        raise

if __name__ == "__main__":
    generate_summaries()