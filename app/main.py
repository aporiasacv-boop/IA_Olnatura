from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router as root_router
from app.api.dynamics.routes import router as dynamics_router
from app.api.sync.routes import router as sync_router
from app.api.analytics.routes import router as analytics_router
from app.api.ai.routes import router as ai_router
from app.api.assistant.routes import router as assistant_router
from app.api.chat.routes import router as chat_router
from app.api.documents.routes import router as documents_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info('Iniciando %s v%s [%s]', settings.APP_NAME, settings.APP_VERSION, settings.APP_ENV)
    yield
    logger.info('Aplicación detenida correctamente')

def create_app() -> FastAPI:
    application = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, description='API del Asistente de Inteligencia Empresarial Olnatura.', debug=settings.DEBUG, lifespan=lifespan)
    application.include_router(root_router)
    application.include_router(dynamics_router, prefix='/dynamics')
    application.include_router(sync_router)
    application.include_router(analytics_router, prefix='/analytics')
    application.include_router(ai_router, prefix='/ai')
    application.include_router(chat_router, prefix='/chat')
    application.include_router(assistant_router, prefix='/assistant')
    application.include_router(documents_router, prefix='/documents')
    return application
app = create_app()
