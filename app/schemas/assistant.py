from pydantic import BaseModel, Field

class AssistantRequest(BaseModel):
    question: str = Field(..., min_length=1, description='Pregunta empresarial del usuario', examples=['¿Cuál es el objeto social de la empresa?'])

class AssistantResponse(BaseModel):
    source: str = Field(..., description='Fuente de la respuesta: analytics, documents, executive o hybrid')
    answer: str = Field(..., description='Respuesta en lenguaje natural generada por Ollama')

class HybridAnalysisRequest(BaseModel):
    question: str = Field(..., min_length=1, description='Pregunta hibrida empresarial', examples=['¿Cuántos clientes tenemos y cómo se registran?'])

class HybridAnalysisResponse(BaseModel):
    confidence: str = Field(..., description='Nivel de confianza hibrida: HIGH, MEDIUM o LOW')
    sources: list[str] = Field(default_factory=list, description='Documentos y fuentes relacionadas')
    answer: str = Field(..., description='Respuesta integrada empresarial')
