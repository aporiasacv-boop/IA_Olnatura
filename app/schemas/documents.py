"""
Schemas para indexación y consulta RAG de documentos.
"""

from typing import Any

from pydantic import BaseModel, Field


class DocumentIndexResponse(BaseModel):
    """Resultado de indexar un documento."""

    filename: str = Field(..., description="Nombre del archivo indexado")
    chunks_indexed: int = Field(..., description="Cantidad de fragmentos indexados")
    status: str = Field(..., description="Estado de la indexación")


class DocumentQueryRequest(BaseModel):
    """Consulta sobre documentos indexados."""

    question: str = Field(
        ...,
        min_length=1,
        description="Pregunta sobre el contenido indexado",
        examples=["¿Cuál es la política de ventas?"],
    )
    top_k: int | None = Field(
        None,
        ge=1,
        le=20,
        description="Cantidad de fragmentos a recuperar (default: configuración RAG)",
    )


class SourceChunkResponse(BaseModel):
    """Fragmento de documento usado como contexto."""

    content: str = Field(..., description="Texto del fragmento")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadatos del fragmento")


class DocumentQueryResponse(BaseModel):
    """Respuesta RAG a una consulta documental."""

    answer: str = Field(..., description="Respuesta generada por el LLM")
    sources: list[SourceChunkResponse] = Field(
        default_factory=list,
        description="Fragmentos recuperados como contexto",
    )
