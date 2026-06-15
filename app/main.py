"""
Punto de entrada de la aplicación FastAPI.

Responsabilidad:
    - Crear e instanciar la aplicación FastAPI.
    - Configurar logging y ciclo de vida.
    - Registrar routers y exponer `app` para uvicorn y pruebas.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router as root_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación.

    Startup: configura logging.
    Shutdown: registra evento de cierre.
    """
    setup_logging()
    logger.info(
        "Iniciando %s v%s [%s]",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.APP_ENV,
    )
    yield
    logger.info("Aplicación detenida correctamente")


def create_app() -> FastAPI:
    """
    Factory que construye y configura la instancia de FastAPI.

    Patrón recomendado para facilitar pruebas y múltiples configuraciones.
    """
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="API del Asistente de Inteligencia Empresarial Olnatura.",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    application.include_router(root_router)

    return application


# Instancia global consumida por uvicorn: uvicorn app.main:app
app = create_app()
