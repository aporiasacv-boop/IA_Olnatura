import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.api.deps import get_semantic_search_service
from app.services.document_context_service import DocumentContextService
from app.services.document_insights_service import DocumentInsightsService

def main() -> int:
    print('=== VALIDACION RAG EMPRESARIAL ===')
    semantic_search = get_semantic_search_service()
    metadata = semantic_search.get_metadata_entries()
    print('documentos_indexados:', len(metadata))
    if metadata:
        sample = next(iter(metadata.values()))
        print('metadata_ejemplo:', json.dumps(sample.to_dict(), ensure_ascii=False, indent=2))
    queries = [
        '¿Qué hace el analista de procesos?',
        'objeto social de la empresa',
    ]
    context_service = DocumentContextService(semantic_search)
    insights_service = DocumentInsightsService()
    for query in queries:
        print(f'\n--- query: {query} ---')
        context = context_service.build_context(query)
        insights = insights_service.build_insights(context)
        print('document_context:', json.dumps(context.to_dict(), ensure_ascii=False, indent=2)[:2000])
        print('document_insights:', json.dumps(insights.to_dict(), ensure_ascii=False, indent=2))
        if context.total_matches == 0:
            print('ADVERTENCIA: sin coincidencias para', query, file=sys.stderr)
    if not any(context_service.build_context(q).total_matches > 0 for q in queries):
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
