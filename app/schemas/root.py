"""
Schema de respuesta para el endpoint raíz GET /.
"""

from pydantic import BaseModel, Field


class RootResponse(BaseModel):
    """Información básica de bienvenida de la API."""

    message: str = Field(..., description="Mensaje de bienvenida")
    app_name: str = Field(..., description="Nombre de la aplicación")
    version: str = Field(..., description="Versión desplegada")
    docs_url: str = Field(..., description="Ruta a la documentación interactiva")
