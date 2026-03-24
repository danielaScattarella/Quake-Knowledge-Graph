# config/config.py
import os
from dotenv import load_dotenv
load_dotenv(override=True)

# Qdrant
from qdrant_client import QdrantClient
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "repo_chunks")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "384"))

qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# Cohere
import cohere # type: ignore
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(COHERE_API_KEY)

# Jina
JINA_API_KEY = os.getenv("JINA_API_KEY")
JINA_EMBEDDING_MODEL = os.getenv("JINA_EMBEDDING_MODEL", "jina-embeddings-v3")