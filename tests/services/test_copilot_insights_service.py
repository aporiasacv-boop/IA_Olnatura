from app.services.copilot_insights_service import CopilotInsightsService

def _executive(
    top_customer_share: float = 42.0,
    top_5_customer_share: float = 85.0,
    top_product_share: float = 45.0,
    invoice_rate: float = 100.0,
    dominant_customer: str = 'Farmacias de Similares',
    dominant_product: str = 'ARISTOCAPS-RB',
) -> dict[str, object]:
    revenue_concentration = 'Concentracion comercial moderada'
    if top_customer_share >= 50:
        revenue_concentration = 'Alta concentracion comercial'
    return {
        'top_customer_share': top_customer_share,
        'top_5_customer_share': top_5_customer_share,
        'top_product_share': top_product_share,
        'invoice_rate': invoice_rate,
        'dominant_customer': dominant_customer,
        'dominant_product': dominant_product,
        'revenue_concentration': revenue_concentration,
        'risk_flags': ['Concentracion comercial moderada'],
    }

def test_moderate_concentration_generates_review() -> None:
    insights = CopilotInsightsService().build_insights(
        analytics_snapshot={'financials': {'total_revenue': '1000.00'}},
        executive_insights=_executive(top_customer_share=42.0),
        hybrid_insights={'confidence': 'MEDIUM'},
    )
    assert 'Revisar periodicamente la dependencia de los principales clientes.' in insights.recommended_reviews
    assert any('moderada' in item.lower() for item in insights.observations)

def test_high_concentration_generates_monitoring_review() -> None:
    insights = CopilotInsightsService().build_insights(
        analytics_snapshot={},
        executive_insights=_executive(top_customer_share=55.0),
        hybrid_insights={},
    )
    assert 'Monitorear riesgo comercial asociado al cliente dominante.' in insights.recommended_reviews

def test_top_five_share_generates_diversification_review() -> None:
    insights = CopilotInsightsService().build_insights(
        analytics_snapshot={},
        executive_insights=_executive(top_5_customer_share=90.0),
        hybrid_insights={},
    )
    assert 'Analizar diversificacion de cartera.' in insights.recommended_reviews

def test_dominant_product_generates_product_review() -> None:
    insights = CopilotInsightsService().build_insights(
        analytics_snapshot={},
        executive_insights=_executive(top_product_share=45.0),
        hybrid_insights={},
    )
    assert 'Revisar dependencia de ingresos respecto al producto principal.' in insights.recommended_reviews
    assert 'Dependencia del producto principal' in insights.attention_points

def test_low_document_confidence_generates_validation_review() -> None:
    insights = CopilotInsightsService().build_insights(
        analytics_snapshot={},
        executive_insights=_executive(),
        hybrid_insights={'document_confidence_level': 'LOW'},
    )
    assert 'Validar documentacion adicional relacionada.' in insights.recommended_reviews

def test_low_invoice_rate_generates_billing_review() -> None:
    insights = CopilotInsightsService().build_insights(
        analytics_snapshot={},
        executive_insights=_executive(invoice_rate=60.0),
        hybrid_insights={},
    )
    assert 'Revisar pedidos pendientes de facturacion.' in insights.recommended_reviews
