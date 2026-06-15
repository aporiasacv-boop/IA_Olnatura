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


@lru_cache
def get_settings() -> Settings:
    """
    Retorna una instancia singleton de Settings.

    El cache evita re-leer variables de entorno en cada request.
    """
    return Settings()


# Instancia conveniente para importación directa
settings = get_settings()
