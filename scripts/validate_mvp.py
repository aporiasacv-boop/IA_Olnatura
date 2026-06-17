import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sqlalchemy import inspect, text
from app.core.config import settings
from app.db.schema import ensure_database_schema
from app.db.session import SessionLocal, engine
from app.domain.chat import ChatIntent
from app.rag.factory import create_embeddings, create_vector_store
from app.services.question_classifier import QuestionClassifier
from app.services.semantic_search_service import SemanticSearchService

def main() -> int:
    print('=== VALIDACION MVP OLNATURA ===')
    print()

    print('[1] Esquema PostgreSQL')
    ensure_database_schema(engine)
    tables = set(inspect(engine).get_table_names())
    print('  tablas:', sorted(tables))
    assert 'ventas' in tables, 'Falta tabla ventas'
    with engine.connect() as conn:
        ventas_count = conn.execute(text('SELECT COUNT(*) FROM ventas')).scalar()
    print('  SELECT COUNT(*) FROM ventas =', ventas_count)
    print('  OK')
    print()

    print('[2] Clasificador de intenciones')
    classifier = QuestionClassifier()
    checks = {
        '¿Cuántos clientes tenemos?': ChatIntent.CUSTOMERS_COUNT,
        '¿Cuántos pedidos tenemos?': ChatIntent.SALES_COUNT,
        '¿Quiénes son nuestros principales clientes?': ChatIntent.TOP_CUSTOMERS,
        '¿Cuál es el cliente que más compra?': ChatIntent.TOP_CUSTOMERS,
        'Muéstrame los clientes más importantes': ChatIntent.TOP_CUSTOMERS,
    }
    for question, expected in checks.items():
        intent = classifier.resolve_intent(question)
        status = 'OK' if intent == expected else 'FAIL'
        print(f'  {status} {question!r} -> {intent.value}')
        if intent != expected:
            return 1
    print()

    print('[3] Documentos en data/documents')
    docs_dir = Path(settings.DOCUMENTS_DIR)
    files = sorted(path.name for path in docs_dir.iterdir() if path.is_file() and path.suffix.lower() == '.txt')
    print('  archivos:', files)
    if not files:
        print('  FAIL sin documentos txt')
        return 1
    print('  OK')
    print()

    print('[4] Indexacion y busqueda semantica (Ollama embeddings)')
    embeddings = create_embeddings()
    vector_store = create_vector_store(embeddings)
    service = SemanticSearchService(
        vector_store=vector_store,
        documents_dir=docs_dir,
        app_settings=settings,
    )
    index_result = service.index_all()
    chunks = vector_store.count_chunks()
    print(f'  index documents={index_result.documents} chunks_nuevos={index_result.chunks} total_chunks={chunks}')
    if chunks <= 0:
        print('  FAIL coleccion Chroma vacia')
        return 1

    queries = [
        '¿Qué hace el analista de procesos?',
        '¿Cuál es el objeto social de la empresa?',
    ]
    for query in queries:
        result = service.search(query)
        print(f'  query={query!r} hits={len(result.results)}')
        if not result.results:
            print('  FAIL sin resultados')
            return 1
        top = result.results[0]
        print(f'    top document={top.document} score={top.score}')
        print(f'    snippet={top.content[:120].replace(chr(10), " ")}...')
    print('  OK')
    print()

    print('[5] ChatService analytics (top clientes)')
    from app.repositories.analytics_repository import AnalyticsRepository
    from app.services.chat_service import ChatService
    from app.services.analytics_service import AnalyticsService
    db = SessionLocal()
    try:
        chat = ChatService(AnalyticsService(AnalyticsRepository(db)))
        result = chat.process('¿Quiénes son nuestros principales clientes?')
        print(f'  intent={result.intent.value} data_type={type(result.data).__name__}')
        if result.intent is not ChatIntent.TOP_CUSTOMERS:
            print('  FAIL intent incorrecto')
            return 1
        print('  OK')
    finally:
        db.close()

    print()
    print('VALIDACION COMPLETA: OK')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
