"""
Configuration settings for Whisky Goggles.
"""
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# File paths
WHISKY_DATABASE_PATH = "data/baxus_whisky_database.csv"
ANNOTATIONS_DIR = "data/annotations"
ROBOFLOW_MAPPING_PATH = "data/roboflow_annotation_mapping.json"
FALLBACK_MAPPING_PATHS = [
    "data/roboflow_comprehensive_mapping.json",
    "data/roboflow_fallback_mapping.json"
]

# Load OpenAI API Key
def load_openai_api_key():
    """Load OpenAI API key from environment or openai.env file."""
    # First check environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    
    # If not found, try to load from file
    if not api_key:
        try:
            # Try multiple possible environment files
            env_files = [
                os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "openai.env")),
                os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "direct_key.env"))
            ]
            
            for env_path in env_files:
                if os.path.exists(env_path):
                    logger.info(f"Loading API key from: {env_path}")
                    try:
                        with open(env_path, 'r') as f:
                            for line in f.readlines():
                                line = line.strip()
                                if line.startswith("OPENAI_API_KEY="):
                                    api_key = line.split("=", 1)[1]
                                    logger.info(f"Found API key in file, length: {len(api_key)} characters")
                                    
                                    # Remove quotes if present
                                    if (api_key.startswith('"') and api_key.endswith('"')) or \
                                       (api_key.startswith("'") and api_key.endswith("'")):
                                        api_key = api_key[1:-1]
                                        logger.info("Removed quotes from API key")
                                    
                                    # Check if key is valid
                                    if len(api_key) > 20 and (api_key.startswith('sk-') or api_key.startswith('sk-proj-')):
                                        return api_key
                    except UnicodeDecodeError:
                        # Try with different encoding
                        logger.warning(f"Unicode decode error with {env_path}, trying different encoding")
                        with open(env_path, 'r', encoding='utf-16') as f:
                            for line in f.readlines():
                                line = line.strip()
                                if line.startswith("OPENAI_API_KEY="):
                                    api_key = line.split("=", 1)[1]
                                    logger.info(f"Found API key with UTF-16 encoding, length: {len(api_key)} characters")
                                    if len(api_key) > 20 and (api_key.startswith('sk-') or api_key.startswith('sk-proj-')):
                                        return api_key
        except Exception as e:
            logger.error(f"Error reading API key from file: {str(e)}")
            logger.error(traceback.format_exc())
    
    # For development, hardcode the key if needed but ensure it's secure in production
    if not api_key:
        # Do not use hardcoded API keys
        logger.error("No OpenAI API key found in environment variables or config files.")
        logger.error("Please set the OPENAI_API_KEY environment variable or create an openai.env file.")
        return None
    
    # Log key status (safely)
    key_prefix = api_key[:4] + "..." if api_key and len(api_key) > 10 else "invalid"
    logger.info(f"Using OpenAI API key with prefix: {key_prefix}")
    
    return api_key
