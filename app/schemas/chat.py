"""
Schemas para el orquestador de chat empresarial.
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Pregunta empresarial en lenguaje natural."""

    question: str = Field(
        ...,
        min_length=1,
        description="Pregunta del usuario",
        examples=["¿Cuáles fueron las ventas del mes?"],
    )


class ChatResponse(BaseModel):
    """Respuesta generada por el orquestador."""

    answer: str = Field(..., description="Respuesta a la pregunta empresarial")
