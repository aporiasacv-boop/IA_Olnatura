"""
Schemas para endpoints de inteligencia artificial.
"""

from pydantic import BaseModel, Field


class AITestRequest(BaseModel):
    """Solicitud de prueba al modelo Ollama."""

    prompt: str = Field(..., min_length=1, description="Texto de entrada para el modelo", examples=["Hola"])


class AITestResponse(BaseModel):
    """Respuesta generada por el modelo Ollama."""

    response: str = Field(..., description="Texto generado por el modelo")


class BusinessSummaryRequest(BaseModel):
    """Indicadores empresariales para interpretación."""

    ventas_mes: float = Field(
        ...,
        ge=0,
        description="Monto total de ventas del mes",
        examples=[125000],
    )
    clientes: int = Field(
        ...,
        ge=0,
        description="Cantidad total de clientes",
        examples=[230],
    )


class BusinessSummaryResponse(BaseModel):
    """Interpretación empresarial generada por el modelo."""

    summary: str = Field(..., description="Interpretación neutral y resumen de los indicadores")
