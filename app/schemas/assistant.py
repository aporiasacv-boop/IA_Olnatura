from pydantic import BaseModel, Field

class AssistantRequest(BaseModel):
    question: str = Field(..., min_length=1, description='Pregunta empresarial del usuario', examples=['¿Cuál es el objeto social de la empresa?'])

class AssistantResponse(BaseModel):
    source: str = Field(..., description='Fuente de la respuesta: analytics, documents o hybrid')
    answer: str = Field(..., description='Respuesta en lenguaje natural generada por Ollama')
