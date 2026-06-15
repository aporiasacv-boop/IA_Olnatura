"""
Router principal de la API v1.

Consolida todos los sub-routers de endpoints bajo un único prefijo /api/v1.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health

api_v1_router = APIRouter()

# Registro de routers por dominio funcional
api_v1_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"],
)
