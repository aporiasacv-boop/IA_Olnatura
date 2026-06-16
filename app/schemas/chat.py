from typing import Any
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description='Pregunta del usuario', examples=['¿Cuántos clientes tenemos?'])

class ChatResponse(BaseModel):
    question: str = Field(..., description='Pregunta original del usuario')
    intent: str = Field(..., description='Intención detectada por el clasificador')
    data: dict[str, Any] | list[dict[str, Any]] | None = Field(None, description='Datos analíticos asociados a la intención')

class ChatNaturalResponse(BaseModel):
    question: str = Field(..., description='Pregunta original del usuario')
    intent: str = Field(..., description='Intención detectada por el clasificador')
    answer: str = Field(..., description='Respuesta en lenguaje natural generada por Ollama')
