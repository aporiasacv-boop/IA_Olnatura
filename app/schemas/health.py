"""
Schemas para el endpoint de health check.

Los schemas Pydantic documentan y validan la estructura de respuestas
expuestas por la API sin acoplar la capa de presentación a la BD.
"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Respuesta estándar del health check de la API."""

    status: str = Field(..., description="Estado del servicio", examples=["ok"])
    app_name: str = Field(..., description="Nombre de la aplicación")
    version: str = Field(..., description="Versión desplegada")
