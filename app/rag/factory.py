from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings
from app.core.config import Settings, settings
from app.rag.vector_store import ChromaVectorStore

def create_embeddings(app_settings: Settings | None=None) -> Embeddings:
    config = app_settings or settings
    return OllamaEmbeddings(model=config.OLLAMA_EMBEDDING_MODEL, base_url=config.OLLAMA_BASE_URL)

def create_vector_store(embeddings: Embeddings, app_settings: Settings | None=None) -> ChromaVectorStore:
    config = app_settings or settings
    return ChromaVectorStore(persist_directory=config.CHROMA_PERSIST_DIR, collection_name=config.CHROMA_COLLECTION_NAME, embeddings=embeddings)
