from pydantic import BaseModel, Field

class DocumentIndexResponse(BaseModel):
    documents: int = Field(..., description='Documentos presentes en el indice')
    chunks: int = Field(..., description='Fragmentos indexados en la ejecucion actual')
    status: str = Field(..., description='Estado de la indexacion')

class DocumentQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description='Consulta semantica sobre documentos indexados', examples=['objeto social de la empresa'])
    top_k: int | None = Field(None, ge=1, le=20, description='Cantidad de fragmentos a recuperar')

class SemanticSearchResultItem(BaseModel):
    document: str = Field(..., description='Nombre del documento fuente')
    score: float = Field(..., description='Puntuacion de similitud normalizada')
    content: str = Field(..., description='Fragmento recuperado')

class DocumentQueryResponse(BaseModel):
    query: str = Field(..., description='Consulta realizada')
    results: list[SemanticSearchResultItem] = Field(default_factory=list, description='Resultados semanticos ordenados por relevancia')

class DocumentsListResponse(BaseModel):
    documents: list[str] = Field(default_factory=list, description='Nombres de archivos en el catalogo')

class DocumentPreviewResponse(BaseModel):
    document: str = Field(..., description='Nombre del documento')
    preview: str = Field(..., description='Primeros caracteres del contenido extraido')

class DocumentsReloadResponse(BaseModel):
    documents: list[str] = Field(default_factory=list, description='Catalogo actualizado tras el reescaneo')

class DocumentAnalyzeRequest(BaseModel):
    query: str = Field(..., min_length=1, description='Pregunta sobre documentos indexados', examples=['¿Qué hace el analista de procesos?'])

class DocumentAnalyzeResponse(BaseModel):
    confidence_level: str = Field(..., description='Nivel de confianza documental: HIGH, MEDIUM o LOW')
    sources: list[str] = Field(default_factory=list, description='Documentos fuente utilizados')
    answer: str = Field(..., description='Respuesta empresarial basada en documentos')
