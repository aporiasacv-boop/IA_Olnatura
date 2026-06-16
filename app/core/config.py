from functools import lru_cache
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=True, extra='ignore')
    APP_ENV: str = 'development'
    APP_NAME: str = 'Asistente de Inteligencia Empresarial Olnatura'
    APP_VERSION: str = '0.1.0'
    DEBUG: bool = True
    HOST: str = '0.0.0.0'
    PORT: int = 8000
    LOG_LEVEL: str = 'INFO'
    DATABASE_URL: str = 'postgresql://postgres:postgres@localhost:5432/olnatura_ai'
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_PRE_PING: bool = True
    D365_BASE_URL: str = 'https://example.operations.dynamics.com/data'
    D365_TENANT_ID: str = ''
    D365_CLIENT_ID: str = ''
    D365_CLIENT_SECRET: str = ''
    D365_TOKEN_URL: str = ''
    D365_OAUTH_SCOPE: str = ''
    D365_HEALTH_ENTITY: str = 'Companies'
    D365_REQUEST_TIMEOUT: float = 30.0
    D365_CLIENTES_ENTITY: str = 'CustomersV3'
    D365_VENTAS_ENTITY: str = 'SalesOrderHeadersV2'
    D365_VENTAS_ENTITY_LABEL: str = 'D365SalesOrderHeaders'
    SYNC_CLIENTES_MAX_RECORDS: int = 100
    SYNC_VENTAS_MAX_RECORDS: int = 100
    ETL_PAGE_SIZE: int = 100
    ETL_MAX_RETRIES: int = 3
    ETL_RETRY_BASE_DELAY: float = 1.0
    OLLAMA_BASE_URL: str = 'http://localhost:11434'
    OLLAMA_MODEL: str = 'llama3.2'
    OLLAMA_EMBEDDING_MODEL: str = 'nomic-embed-text'
    OLLAMA_REQUEST_TIMEOUT: float = 120.0
    CHROMA_PERSIST_DIR: str = './data/chroma'
    CHROMA_COLLECTION_NAME: str = 'olnatura_documents'
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 200
    RAG_TOP_K: int = 4

    @property
    def d365_token_url(self) -> str:
        if self.D365_TOKEN_URL:
            return self.D365_TOKEN_URL
        return f'https://login.microsoftonline.com/{self.D365_TENANT_ID}/oauth2/v2.0/token'

    @property
    def d365_oauth_scope(self) -> str:
        if self.D365_OAUTH_SCOPE:
            return self.D365_OAUTH_SCOPE
        resource_url = self.D365_BASE_URL.removesuffix('/data').rstrip('/')
        return f'{resource_url}/.default'

@lru_cache
def get_settings() -> Settings:
    return Settings()
settings = get_settings()
