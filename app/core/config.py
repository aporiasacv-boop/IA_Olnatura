"""
Configuración centralizada de la aplicación.

Utiliza pydantic-settings para cargar variables de entorno
desde el sistema o desde un archivo .env (mediante python-dotenv).
"""

from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Carga variables del archivo .env al iniciar el módulo
load_dotenv()


class Settings(BaseSettings):
    """
    Modelo de configuración tipado.

    Cada atributo se mapea a una variable de entorno.
    Los valores por defecto permiten desarrollo local sin .env completo.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Aplicación ---
    APP_ENV: str = "development"
    APP_NAME: str = "Asistente de Inteligencia Empresarial Olnatura"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # --- Servidor ---
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # --- Logging ---
    LOG_LEVEL: str = "INFO"

    # --- Base de datos PostgreSQL ---
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/olnatura_ai"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_PRE_PING: bool = True

    # --- Dynamics 365 Finance & Operations (OData) ---
    D365_BASE_URL: str = "https://example.operations.dynamics.com/data"
    D365_TENANT_ID: str = ""
    D365_CLIENT_ID: str = ""
    D365_CLIENT_SECRET: str = ""
    D365_TOKEN_URL: str = ""
    D365_OAUTH_SCOPE: str = ""
    D365_HEALTH_ENTITY: str = "Companies"
    D365_REQUEST_TIMEOUT: float = 30.0
    D365_CLIENTES_ENTITY: str = "CustomersV3"
    D365_VENTAS_ENTITY: str = "SalesOrderHeadersV2"

    # --- ETL ---
    ETL_PAGE_SIZE: int = 100
    ETL_MAX_RETRIES: int = 3
    ETL_RETRY_BASE_DELAY: float = 1.0

    # --- Ollama (LLM local) ---
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"
    OLLAMA_REQUEST_TIMEOUT: float = 120.0

    # --- RAG (ChromaDB + LangChain) ---
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    CHROMA_COLLECTION_NAME: str = "olnatura_documents"
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 200
    RAG_TOP_K: int = 4

    @property
    def d365_token_url(self) -> str:
        """URL del endpoint OAuth de Azure AD."""
        if self.D365_TOKEN_URL:
            return self.D365_TOKEN_URL
        return f"https://login.microsoftonline.com/{self.D365_TENANT_ID}/oauth2/v2.0/token"

    @property
    def d365_oauth_scope(self) -> str:
        """Scope OAuth para client credentials (.default)."""
        if self.D365_OAUTH_SCOPE:
            return self.D365_OAUTH_SCOPE
        resource_url = self.D365_BASE_URL.removesuffix("/data").rstrip("/")
        return f"{resource_url}/.default"


@lru_cache
def get_settings() -> Settings:
    """
    Retorna una instancia singleton de Settings.

    El cache evita re-leer variables de entorno en cada request.
    """
    return Settings()


# Instancia conveniente para importación directa
settings = get_settings()
