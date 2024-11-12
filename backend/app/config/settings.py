# File: app/config/settings.py
import os
from dotenv import load_dotenv

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
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '400'))

# Retrieval settings
RETRIEVAL_MODE = os.getenv('RETRIEVAL_MODE', 'mmr')  # 'similarity' or 'mmr'
MMR_DIVERSITY_SCORE = float(os.getenv('MMR_DIVERSITY_SCORE', '0.3'))

# Cache settings
ENABLE_CACHE = os.getenv('ENABLE_CACHE', 'True').lower() in ('true', '1', 't')
CACHE_DIR = os.getenv('CACHE_DIR', '.cache')

# Document processing settings
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
RETRY_DELAY = float(os.getenv('RETRY_DELAY', '1.0'))
MIN_CHUNK_SIZE = int(os.getenv('MIN_CHUNK_SIZE', '100'))
MAX_CHUNK_SIZE = int(os.getenv('MAX_CHUNK_SIZE', '3000'))