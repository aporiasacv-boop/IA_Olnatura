from pydantic import BaseModel, Field

class GovernanceRequest(BaseModel):
    question: str = Field(..., min_length=1, description='Pregunta de trazabilidad empresarial', examples=['¿Qué evidencia tienes?'])

class GovernanceResponse(BaseModel):
    confidence: str = Field(..., description='Nivel de confianza: HIGH, MEDIUM o LOW')
    evidence: list[str] = Field(default_factory=list, description='Evidencia verificable asociada a la respuesta')
    answer: str = Field(..., description='Respuesta gobernada con trazabilidad')
    source_type: str | None = Field(None, description='Tipo de fuente principal')
    source_tables: list[str] = Field(default_factory=list, description='Tablas PostgreSQL consultadas')
    source_documents: list[str] = Field(default_factory=list, description='Documentos indexados consultados')
    snapshot_date: str | None = Field(None, description='Fecha del snapshot analitico')
    records_analyzed: int | None = Field(None, description='Registros analizados')
    generated_at: str | None = Field(None, description='Fecha de generacion del contexto de gobernanza')
