"""
Configuration settings for Optimized Claude Memory System
"""

# Persona settings
PERSONA_NAME = "Claude"
PERSONA_DESCRIPTION = "An AI assistant with long-term memory capabilities."

# Memory system settings
MEMORY_SEARCH_TOP_K = 5  # Number of memories to retrieve in standard queries
DEEP_SEARCH_TOP_K = 10   # Number of memories for deep searches
MAX_FILE_SIZE_KB = 200   # Maximum size of memories file in KB
ARCHIVE_THRESHOLD = 100  # Size in KB at which to start archiving older memories

# Embedding settings
EMBEDDING_MODEL = "sentence-transformer"  # Options: "openai", "sentence-transformer", "fallback"
OPENAI_API_KEY = ""  # Only needed if using OpenAI embeddings

# Memory preprocessing
MAX_MEMORY_WORDS = 25  # Maximum words to keep in memory for embedding
USE_TAGS = True        # Whether to use semantic tagging for memory classification

# ChromaDB settings
USE_CHROMADB = True    # Whether to use ChromaDB for vector storage
CHROMA_PERSIST_DIR = "memory_store/.chroma"  # Directory for ChromaDB persistence
