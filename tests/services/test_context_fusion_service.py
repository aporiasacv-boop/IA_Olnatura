from app.services.context_fusion_service import ContextFusionService

def test_fuse_combines_analytics_and_documents() -> None:
    service = ContextFusionService()
    fused = service.fuse(
        intent='customers_count',
        analytics_data={'total_customers': 100},
        document_results=[{'document': 'Manual.pdf', 'score': 0.9, 'content': 'Registro en ventas.'}],
    )
    assert fused.analytics_intent == 'customers_count'
    assert fused.analytics_data == {'total_customers': 100}
    assert fused.document_hits == 1
    assert fused.analytics_hits == 1

def test_fuse_document_hits_zero_when_no_results() -> None:
    service = ContextFusionService()
    fused = service.fuse(
        intent='sales_count',
        analytics_data={'total_sales_orders': 5},
        document_results=[],
    )
    assert fused.document_hits == 0
    assert fused.analytics_hits == 1
