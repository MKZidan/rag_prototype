"""
Configuration settings for the pgvector knowledge base system.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5435)),
    'database': os.getenv('DB_NAME', 'knowledge_base'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '0')
}


# Ollama Configuration
OLLAMA_CONFIG = {
    'base_url': os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
    'model': os.getenv('OLLAMA_EMBEDDING_MODEL', 'nomic-embed-text'),
    'dimension': int(os.getenv('EMBEDDING_DIMENSION', 768))
}

# Text Processing Configuration
TEXT_CONFIG = {
    'chunk_size': int(os.getenv('CHUNK_SIZE', 1000)),
    'chunk_overlap': int(os.getenv('CHUNK_OVERLAP', 100)),
    'data_directory': str(os.getenv('DATA_DIERECTORY', './news_articles'))
}

# Search Configuration
SEARCH_CONFIG = {
    'default_threshold': float(os.getenv('DEFAULT_MATCH_THRESHOLD', 0.5)),
    'default_count': int(os.getenv('DEFAULT_MATCH_COUNT', 3))
}

# Hugging Face Configuration
HUGGINGFACE_CONFIG = {
    'embedding_model': os.getenv('HUGGINGFACE_MODEL', 'sentence-transformers/all-mpnet-base-v2')
}

OPENROUTER_CONFIG = {
    'base_url': os.getenv('OPEN_ROUTER_URL', 'https://openrouter.ai/api/v1'),
    'api_key': os.getenv('OPEN_ROUTER_API_KEY', 'your_api_key'),
    'chat_model': os.getenv('CHAT_MODEL', 'meta-llama/llama-3.1-8b-instruct')
}

# Validation
def validate_config():
    """Validate that required configuration is present."""
    if not DB_CONFIG['password']:
        raise ValueError("DB_PASSWORD must be set in environment variables")
    
    if OLLAMA_CONFIG['dimension'] not in [1536, 768, 3072]:
        raise ValueError("EMBEDDING_DIMENSION must be 1536, 768, or 3072")
    
    return True

# Database connection string
def get_db_connection_string():
    """Get database connection string."""
    return f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

