import logging
import pkg_resources
from packaging import version

logger = logging.getLogger(__name__)

REQUIRED_VERSIONS = {
    'flask': '2.3.2',
    'flask-cors': '3.0.10',
    'python-dotenv': '1.0.0',
    'pydantic': '1.10.18',
    'anthropic': '0.17.0',
    'langsmith': '0.0.87',
    'langchain-core': '0.1.23',
    'langchain': '0.0.311',
    'langchain-anthropic': '0.1.1',
    'langchain-community': '0.0.13',
    'chromadb': '0.3.29',
    'cohere': '4.37',
    'gunicorn': '20.1.0',
    'tiktoken': '0.8.0',  # Updated to match your installed version
    'pypdf': '3.9.0'
}

def check_versions():
    """Check if installed package versions meet minimum requirements"""
    mismatched = []
    missing = []
    
    for package, required_version in REQUIRED_VERSIONS.items():
        try:
            installed_version = pkg_resources.get_distribution(package).version
            if version.parse(installed_version) < version.parse(required_version):
                mismatched.append(f"{package}: required>={required_version}, installed={installed_version}")
        except pkg_resources.DistributionNotFound:
            missing.append(package)
    
    if missing:
        logger.warning(f"Missing packages: {', '.join(missing)}")
    if mismatched:
        logger.warning("Version mismatches found:")
        for mismatch in mismatched:
            logger.warning(mismatch)
    
    return not (missing or mismatched)