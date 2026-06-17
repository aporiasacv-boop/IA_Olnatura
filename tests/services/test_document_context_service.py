from unittest.mock import MagicMock

from app.domain.document_context import DocumentContext
from app.services.document_context_service import DocumentContextService
from app.services.semantic_search_service import SemanticSearchHit, SemanticSearchResult

def test_build_context_enriches_search_results() -> None:
    semantic_search = MagicMock()
    semantic_search.search.return_value = SemanticSearchResult(
        query='analista de procesos',
        results=[
            SemanticSearchHit(
                document='Manual_Analista_Procesos.pdf',
                score=0.91,
                content='El analista de procesos documenta y mejora procesos.',
            ),
            SemanticSearchHit(
                document='Acta_Constitutiva.pdf',
                score=0.82,
                content='Fragmento complementario.',
            ),
        ],
    )
    semantic_search.get_metadata_entries.return_value = {}
    service = DocumentContextService(semantic_search)
    context = service.build_context('¿Qué hace el analista de procesos?')
    assert context.total_matches == 2
    assert context.top_document == 'Manual_Analista_Procesos.pdf'
    assert context.sources == ['Manual_Analista_Procesos.pdf', 'Acta_Constitutiva.pdf']
    assert context.average_score == 0.86
    assert context.documents[0]['document_type'] == 'manual'
    assert 'Manual_Analista_Procesos.pdf' in context.context

def test_build_context_returns_empty_when_no_matches() -> None:
    semantic_search = MagicMock()
    semantic_search.search.return_value = SemanticSearchResult(query='sin resultados', results=[])
    semantic_search.get_metadata_entries.return_value = {}
    service = DocumentContextService(semantic_search)
    context = service.build_context('pregunta sin match')
    assert context.total_matches == 0
    assert context.top_document is None
    assert context.context == ''
