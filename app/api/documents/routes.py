import tempfile
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from app.api.deps import get_rag_service
from app.core.logging import get_logger
from app.integrations.ollama.exceptions import OllamaError
from app.rag.exceptions import RAGError, UnsupportedDocumentError
from app.rag.loaders import validate_extension
from app.schemas.documents import DocumentIndexResponse, DocumentQueryRequest, DocumentQueryResponse, SourceChunkResponse
from app.services.rag_service import RAGService
router = APIRouter()
logger = get_logger(__name__)

@router.post('/index', response_model=DocumentIndexResponse, summary='Indexar documento PDF o DOCX', tags=['Documents'])
async def index_document(file: UploadFile=File(..., description='Archivo PDF o DOCX a indexar'), service: RAGService=Depends(get_rag_service)) -> DocumentIndexResponse:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='El archivo debe incluir nombre.')
    try:
        validate_extension(file.filename)
    except UnsupportedDocumentError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    suffix = Path(file.filename).suffix.lower()
    logger.info('Indexando documento: %s', file.filename)
    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        result = service.index_file(tmp_path, file.filename)
    except RAGError as exc:
        logger.error('Error indexando documento: %s', exc.message)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message) from exc
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)
    return DocumentIndexResponse(filename=result.filename, chunks_indexed=result.chunks_indexed, status=result.status)

@router.post('/query', response_model=DocumentQueryResponse, summary='Consultar documentos indexados (RAG)', tags=['Documents'])
def query_documents(request: DocumentQueryRequest, service: RAGService=Depends(get_rag_service)) -> DocumentQueryResponse:
    logger.info('Consulta RAG recibida')
    try:
        result = service.query(request.question, top_k=request.top_k)
    except OllamaError as exc:
        logger.error('Error LLM en consulta RAG: %s', exc.message)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=exc.message) from exc
    except RAGError as exc:
        logger.error('Error en consulta RAG: %s', exc.message)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message) from exc
    return DocumentQueryResponse(answer=result.answer, sources=[SourceChunkResponse(content=source.content, metadata=source.metadata) for source in result.sources])
