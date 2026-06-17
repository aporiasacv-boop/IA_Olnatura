from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles

from starlette.middleware.sessions import SessionMiddleware

from app.api.routes import router as root_router

from app.api.dynamics.routes import router as dynamics_router

from app.api.sync.routes import router as sync_router

from app.api.analytics.routes import router as analytics_router

from app.api.ai.routes import router as ai_router

from app.api.assistant.routes import router as assistant_router

from app.api.auth.routes import router as auth_router

from app.api.chat.routes import router as chat_router

from app.api.documents.routes import router as documents_router
from app.api.memory.routes import router as memory_router

from app.core.config import settings

from app.core.logging import get_logger, setup_logging

from app.db.bootstrap import bootstrap_users

from app.middleware.auth import AuthenticationMiddleware



logger = get_logger(__name__)

UI_DIR = Path(__file__).resolve().parent.parent / 'web' / 'ui'



@asynccontextmanager

async def lifespan(app: FastAPI):

    setup_logging()

    logger.info('Iniciando %s v%s [%s]', settings.APP_NAME, settings.APP_VERSION, settings.APP_ENV)
    from app.db.session import engine
    from app.db.schema import ensure_database_schema
    ensure_database_schema(engine)
    if settings.AUTH_ENABLED:
        bootstrap_users()

    yield

    logger.info('Aplicación detenida correctamente')



def create_app() -> FastAPI:

    application = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, description='API del Asistente de Inteligencia Empresarial Olnatura.', debug=settings.DEBUG, lifespan=lifespan)

    application.add_middleware(AuthenticationMiddleware)

    application.add_middleware(

        SessionMiddleware,

        secret_key=settings.SESSION_SECRET_KEY,

        max_age=settings.SESSION_MAX_AGE,

        https_only=settings.APP_ENV == 'production',

        same_site='lax',

    )

    application.include_router(root_router)

    application.include_router(auth_router, prefix='/auth')

    application.include_router(dynamics_router, prefix='/dynamics')

    application.include_router(sync_router)

    application.include_router(analytics_router, prefix='/analytics')

    application.include_router(ai_router, prefix='/ai')

    application.include_router(chat_router, prefix='/chat')

    application.include_router(assistant_router, prefix='/assistant')

    application.include_router(documents_router, prefix='/documents')

    application.include_router(memory_router, prefix='/memory')

    if UI_DIR.is_dir():

        application.mount('/ui', StaticFiles(directory=str(UI_DIR), html=True), name='ui')

    return application

app = create_app()


