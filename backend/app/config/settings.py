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

# File: backend/app/config/settings.py

# File: backend/app/config/settings.py

import os
import logging
from typing import Any, Dict
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_env_float(key: str, default: float) -> float:
    """Get float from environment with fallback"""
    try:
        value = os.getenv(key)
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        logger.warning(f"Invalid value for {key}, using default: {default}")
        return default

def get_env_int(key: str, default: int) -> int:
    """Get integer from environment with fallback"""
    try:
        value = os.getenv(key)
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        logger.warning(f"Invalid value for {key}, using default: {default}")
        return default

def get_env_bool(key: str, default: bool) -> bool:
    """Get boolean from environment with fallback"""
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 't')

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Application settings
DEBUG = get_env_bool("FLASK_DEBUG", False)
ALLOWED_ORIGIN = os.getenv('ALLOWED_ORIGIN', 'http://localhost:3000')

# Vector store settings - using get_env_float to handle validation
VECTOR_STORE_SIMILARITY_THRESHOLD = max(0.0, min(1.0, get_env_float('VECTOR_STORE_SIMILARITY_THRESHOLD', 0.3)))
VECTOR_STORE_TOP_K = get_env_int('VECTOR_STORE_TOP_K', 8)

# Embedding settings
EMBEDDING_MODEL = os.getenv('COHERE_MODEL', 'embed-multilingual-v2.0')

# LLM settings
CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-sonnet-20240229')
LLM_TEMPERATURE = max(0.0, min(1.0, get_env_float('LLM_TEMPERATURE', 0.3)))
LLM_MAX_TOKENS = get_env_int('LLM_MAX_TOKENS', 4096)

# Chunking settings
CHUNK_SIZE = get_env_int('CHUNK_SIZE', 2000)
CHUNK_OVERLAP = get_env_int('CHUNK_OVERLAP', 200)

# Retrieval settings
RETRIEVAL_MODE = os.getenv('RETRIEVAL_MODE', 'mmr')
MMR_DIVERSITY_SCORE = max(0.0, min(1.0, get_env_float('MMR_DIVERSITY_SCORE', 0.3)))

# Cache settings
ENABLE_CACHE = get_env_bool('ENABLE_CACHE', True)
CACHE_DIR = os.getenv('CACHE_DIR', '.cache')

# Document processing settings
MAX_RETRIES = get_env_int('MAX_RETRIES', 3)
RETRY_DELAY = get_env_float('RETRY_DELAY', 1.0)
MIN_CHUNK_SIZE = get_env_int('MIN_CHUNK_SIZE', 100)
MAX_CHUNK_SIZE = get_env_int('MAX_CHUNK_SIZE', 8000)

# Special settings for code chunks
CODE_CHUNK_SIZE = get_env_int('CODE_CHUNK_SIZE', 11800)
CODE_CHUNK_OVERLAP = get_env_int('CODE_CHUNK_OVERLAP', 400)
MIN_CODE_CHUNK_SIZE = get_env_int('MIN_CODE_CHUNK_SIZE', 50)
MAX_CODE_CHUNK_SIZE = get_env_int('MAX_CODE_CHUNK_SIZE', 11800)

# Add these to backend/app/config/settings.py


def validate_settings() -> Dict[str, Any]:
    """Validate all settings and return current configuration"""
    try:
        # Check required API keys
        if not ANTHROPIC_API_KEY:
            logger.warning("ANTHROPIC_API_KEY not set")
        if not COHERE_API_KEY:
            logger.warning("COHERE_API_KEY not set")

        # Validate chunk sizes
        if MIN_CHUNK_SIZE >= MAX_CHUNK_SIZE:
            logger.warning("MIN_CHUNK_SIZE must be less than MAX_CHUNK_SIZE")

        if CHUNK_OVERLAP >= CHUNK_SIZE:
            logger.warning("CHUNK_OVERLAP must be less than CHUNK_SIZE")

        # Create cache directory if enabled
        if ENABLE_CACHE:
            os.makedirs(CACHE_DIR, exist_ok=True)

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

        logger.info("Configuration validated successfully")
        return config

    except Exception as e:
        logger.error(f"Configuration validation error: {str(e)}")
        raise

# Validate settings on import
try:
    current_config = validate_settings()
    logger.info("Settings loaded and validated successfully")
except Exception as e:
    logger.error(f"Error in settings validation: {str(e)}")
    raise