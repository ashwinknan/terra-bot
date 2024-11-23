# File: backend/app/config/settings.py

"""
Application configuration loaded from environment variables.

Required Environment Variables:
- ANTHROPIC_API_KEY: API key for Anthropic's Claude LLM
- COHERE_API_KEY: API key for Cohere embeddings
- ALLOWED_ORIGIN: Allowed CORS origin (e.g., http://localhost:3000)

Optional Environment Variables:
- FLASK_DEBUG: Enable debug mode (default: False)
- VECTOR_STORE_TOP_K: Number of results to return (default: 8)
- VECTOR_STORE_SIMILARITY_THRESHOLD: Minimum similarity score (default: 0.3)
- CLAUDE_MODEL: Model version to use (default: claude-3-sonnet-20240229)
- LLM_TEMPERATURE: Temperature for LLM responses (default: 0.3)
- LLM_MAX_TOKENS: Maximum tokens in LLM response (default: 4096)
- CHUNK_SIZE: Size of text chunks (default: 2000)
- CHUNK_OVERLAP: Overlap between chunks (default: 400)
- ENABLE_CACHE: Enable vector store caching (default: True)
- CACHE_DIR: Directory for cache storage (default: .cache)
- MAX_RETRIES: Maximum retry attempts (default: 3)
- RETRY_DELAY: Delay between retries in seconds (default: 1.0)
- MIN_CHUNK_SIZE: Minimum allowed chunk size (default: 100)
- MAX_CHUNK_SIZE: Maximum allowed chunk size (default: 3000)
"""

import os
import logging
from typing import Any, Dict
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Application settings
DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
ALLOWED_ORIGIN = os.getenv('ALLOWED_ORIGIN', 'http://localhost:3000')

# Vector store settings
VECTOR_STORE_SIMILARITY_THRESHOLD = float(os.getenv('VECTOR_STORE_SIMILARITY_THRESHOLD', '0.3'))
VECTOR_STORE_TOP_K = int(os.getenv('VECTOR_STORE_TOP_K', '8'))

# Embedding settings
EMBEDDING_MODEL = os.getenv('COHERE_MODEL', 'embed-multilingual-v2.0')

# LLM settings
CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-sonnet-20240229')
LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.3'))
LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', '4096'))

# Chunking settings
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '2000'))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '200'))

# Retrieval settings
RETRIEVAL_MODE = os.getenv('RETRIEVAL_MODE', 'mmr')  # 'similarity' or 'mmr'
MMR_DIVERSITY_SCORE = float(os.getenv('MMR_DIVERSITY_SCORE', '0.3'))  # Added this line

# Cache settings
ENABLE_CACHE = os.getenv('ENABLE_CACHE', 'True').lower() in ('true', '1', 't')
CACHE_DIR = os.getenv('CACHE_DIR', '.cache')

# Document processing settings
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
RETRY_DELAY = float(os.getenv('RETRY_DELAY', '1.0'))
MIN_CHUNK_SIZE = int(os.getenv('MIN_CHUNK_SIZE', '100'))
MAX_CHUNK_SIZE = int(os.getenv('MAX_CHUNK_SIZE', '8000'))

# Special settings for code chunks
CODE_CHUNK_SIZE = int(os.getenv('CODE_CHUNK_SIZE', '11800'))  # Reduced from 12000 to allow for markers
CODE_CHUNK_OVERLAP = int(os.getenv('CODE_CHUNK_OVERLAP', '400'))
MIN_CODE_CHUNK_SIZE = int(os.getenv('MIN_CODE_CHUNK_SIZE', '50'))
MAX_CODE_CHUNK_SIZE = int(os.getenv('MAX_CODE_CHUNK_SIZE', '11800'))  # Reduced to match CODE_CHUNK_SIZE

def validate_settings() -> Dict[str, Any]:
    """Validate all settings and return current configuration"""
    config = {
        'api_keys': {
            'anthropic': bool(ANTHROPIC_API_KEY),
            'cohere': bool(COHERE_API_KEY),
        },
        'vector_store': {
            'similarity_threshold': VECTOR_STORE_SIMILARITY_THRESHOLD,
            'top_k': VECTOR_STORE_TOP_K,
        },
        'llm': {
            'model': CLAUDE_MODEL,
            'temperature': LLM_TEMPERATURE,
            'max_tokens': LLM_MAX_TOKENS,
        },
        'processing': {
            'chunk_size': CHUNK_SIZE,
            'chunk_overlap': CHUNK_OVERLAP,
            'min_chunk_size': MIN_CHUNK_SIZE,
            'max_chunk_size': MAX_CHUNK_SIZE,
        },
        'cache': {
            'enabled': ENABLE_CACHE,
            'directory': CACHE_DIR,
        }
    }

    # Validation checks
    try:
        assert 0 <= VECTOR_STORE_SIMILARITY_THRESHOLD <= 1, "Similarity threshold must be between 0 and 1"
        assert 0 <= LLM_TEMPERATURE <= 1, "LLM temperature must be between 0 and 1"
        assert MIN_CHUNK_SIZE < MAX_CHUNK_SIZE, "Min chunk size must be less than max chunk size"
        assert CHUNK_OVERLAP < CHUNK_SIZE, "Chunk overlap must be less than chunk size"
        assert VECTOR_STORE_TOP_K > 0, "Top K must be positive"
        assert LLM_MAX_TOKENS > 0, "Max tokens must be positive"
        assert 0 <= MMR_DIVERSITY_SCORE <= 1, "MMR diversity score must be between 0 and 1"
        
        if ENABLE_CACHE:
            os.makedirs(CACHE_DIR, exist_ok=True)
            
        logger.info("Configuration validated successfully")
        return config
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {str(e)}")
        raise

# Validate settings on import
try:
    current_config = validate_settings()
    logger.info("Settings loaded and validated successfully")
except Exception as e:
    logger.error(f"Error in settings validation: {str(e)}")
    raise