from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.deps import get_document_loader_service, get_semantic_search_service
from app.core.logging import get_logger
from app.documents.exceptions import DocumentLoaderError, DocumentNotFoundError
from app.integrations.ollama.exceptions import OllamaError
from app.rag.exceptions import RAGError
from app.schemas.documents import DocumentIndexResponse, DocumentPreviewResponse, DocumentQueryRequest, DocumentQueryResponse, DocumentsListResponse, DocumentsReloadResponse, SemanticSearchResultItem
from app.services.document_loader_service import DocumentLoaderService
from app.services.semantic_search_service import SemanticSearchService

router = APIRouter()
logger = get_logger(__name__)

@router.get('', response_model=DocumentsListResponse, summary='Listar documentos del catalogo', tags=['Documents'])
def list_documents(service: DocumentLoaderService=Depends(get_document_loader_service)) -> DocumentsListResponse:
    return DocumentsListResponse(documents=service.list_documents())

@router.get('/preview', response_model=DocumentPreviewResponse, summary='Vista previa de un documento', tags=['Documents'])
def preview_document(name: str=Query(..., min_length=1, description='Nombre del documento'), service: DocumentLoaderService=Depends(get_document_loader_service)) -> DocumentPreviewResponse:
    try:
        document_name, preview = service.preview(name)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except DocumentLoaderError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message) from exc
    return DocumentPreviewResponse(document=document_name, preview=preview)

@router.post('/reload', response_model=DocumentsReloadResponse, summary='Reescanear carpeta de documentos', tags=['Documents'])
def reload_documents(service: DocumentLoaderService=Depends(get_document_loader_service)) -> DocumentsReloadResponse:
    logger.info('Reescaneo de documentos solicitado via POST /documents/reload')
    documents = service.reload()
    return DocumentsReloadResponse(documents=documents)

@router.post('/index', response_model=DocumentIndexResponse, summary='Indexar documentos de data/documents en ChromaDB', tags=['Documents'])
def index_documents(
    service: SemanticSearchService=Depends(get_semantic_search_service),
    loader: DocumentLoaderService=Depends(get_document_loader_service),
) -> DocumentIndexResponse:
    logger.info('Indexacion semantica solicitada via POST /documents/index')
    loader.reload()
    try:
        result = service.index_all()
    except DocumentLoaderError as exc:
        logger.error('Error extrayendo texto para indexacion: %s', exc.message)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message) from exc
    except RAGError as exc:
        logger.error('Error indexando documentos: %s', exc.message)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message) from exc
    except OllamaError as exc:
        logger.error('Error de embeddings en indexacion: %s', exc.message)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=exc.message) from exc
    return DocumentIndexResponse(documents=result.documents, chunks=result.chunks, status=result.status)

@router.post('/query', response_model=DocumentQueryResponse, summary='Busqueda semantica sobre documentos indexados', tags=['Documents'])
def query_documents(request: DocumentQueryRequest, service: SemanticSearchService=Depends(get_semantic_search_service)) -> DocumentQueryResponse:
    logger.info('Consulta semantica recibida via POST /documents/query')
    try:
        result = service.search(request.query, top_k=request.top_k)
    except OllamaError as exc:
        logger.error('Error de embeddings en consulta semantica: %s', exc.message)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=exc.message) from exc
    except RAGError as exc:
        logger.error('Error en consulta semantica: %s', exc.message)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message) from exc
    return DocumentQueryResponse(query=result.query, results=[SemanticSearchResultItem(document=item.document, score=item.score, content=item.content) for item in result.results])
