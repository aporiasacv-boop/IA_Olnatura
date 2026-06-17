from unittest.mock import MagicMock
from app.services.ai_response_service import AIResponseService

def test_generate_builds_prompt_and_calls_llm() -> None:
    llm = MagicMock()
    llm.generate.return_value = 'Actualmente existen 100 clientes sincronizados.'
    service = AIResponseService(llm)
    answer = service.generate(
        question='¿Cuántos clientes tenemos?',
        intent='customers_count',
        data={'total_customers': 100},
    )
    assert answer == 'Actualmente existen 100 clientes sincronizados.'
    llm.generate.assert_called_once()
    prompt = llm.generate.call_args.args[0]
    assert 'customers_count' in prompt
    assert '"total_customers": 100' in prompt

def test_build_prompt_exposes_prompt_builder() -> None:
    llm = MagicMock()
    service = AIResponseService(llm)
    prompt = service.build_prompt(
        question='¿Cuántos pedidos tenemos?',
        intent='sales_count',
        data={'total_sales_orders': 5},
    )
    assert 'sales_count' in prompt
    assert '"total_sales_orders": 5' in prompt

def test_generate_document_analysis_builds_expert_prompt() -> None:
    llm = MagicMock()
    llm.generate.return_value = 'Segun Manual.pdf, el analista documenta procesos. Nivel de confianza: ALTO.'
    service = AIResponseService(llm)
    answer = service.generate_document_analysis(
        question='¿Qué hace el analista de procesos?',
        document_context={'documents': [], 'sources': ['Manual.pdf'], 'context': 'texto'},
        document_insights={'confidence_level': 'HIGH', 'source_documents': ['Manual.pdf']},
    )
    assert 'analista' in answer
    prompt = llm.generate.call_args.args[0]
    assert 'especialista documental corporativo' in prompt
    assert 'INSIGHTS DOCUMENTALES' in prompt

def test_generate_from_documents_builds_document_prompt() -> None:
    llm = MagicMock()
    llm.generate.return_value = 'El objeto social es comercializar productos naturales.'
    service = AIResponseService(llm)
    answer = service.generate_from_documents(
        question='¿Cuál es el objeto social?',
        results=[{'document': 'Acta.docx', 'score': 0.9, 'content': 'Objeto social...'}],
    )
    assert 'comercializar' in answer
    prompt = llm.generate.call_args.args[0]
    assert 'FRAGMENTOS DOCUMENTALES' in prompt

def test_generate_copilot_response_builds_copilot_prompt() -> None:
    llm = MagicMock()
    llm.generate.return_value = 'Seria conveniente monitorear la concentracion comercial.'
    service = AIResponseService(llm)
    answer = service.generate_copilot_response(
        question='¿Qué debería revisar?',
        copilot_context={'copilot_insights': {'recommended_reviews': ['Revisar clientes']}},
    )
    assert 'concentracion' in answer
    prompt = llm.generate.call_args.args[0]
    assert 'Business Copilot' in prompt
    assert 'copilot_insights' in prompt

def test_generate_hybrid_business_analysis_builds_expert_prompt() -> None:
    llm = MagicMock()
    llm.generate.return_value = 'Hay 100 clientes y se registran segun Manual_Clientes.pdf.'
    service = AIResponseService(llm)
    answer = service.generate_hybrid_business_analysis(
        question='¿Cuántos clientes tenemos y cómo se registran?',
        hybrid_context={'analytics_snapshot': {'summary': {'total_customers': 100}}},
        hybrid_insights={'confidence': 'MEDIUM', 'cross_source_findings': []},
    )
    assert '100 clientes' in answer
    prompt = llm.generate.call_args.args[0]
    assert 'consultor empresarial senior' in prompt
    assert 'CONTEXTO HIBRIDO' in prompt

def test_generate_hybrid_builds_fused_prompt() -> None:
    from app.services.context_fusion_service import FusedContext
    llm = MagicMock()
    llm.generate.return_value = 'Hay 100 clientes y se registran en ventas.'
    service = AIResponseService(llm)
    context = FusedContext(
        analytics_intent='customers_count',
        analytics_data={'total_customers': 100},
        document_results=[{'document': 'Manual.pdf', 'score': 0.9, 'content': 'Registro en ventas.'}],
    )
    answer = service.generate_hybrid(question='¿Cuántos clientes tenemos y cómo se registran?', context=context)
    assert '100 clientes' in answer
    prompt = llm.generate.call_args.args[0]
    assert 'CONTEXTO FUSIONADO' in prompt
    assert 'customers_count' in prompt
    assert 'Manual.pdf' in prompt

def test_generate_business_analysis_builds_analyst_prompt() -> None:
    llm = MagicMock()
    llm.generate.return_value = 'La cartera presenta concentracion relevante en pocos clientes.'
    service = AIResponseService(llm)
    snapshot = {
        'summary': {'total_customers': 100, 'total_orders': 100},
        'insights': {'largest_customer_share': 42.5},
    }
    answer = service.generate_business_analysis(
        question='Dame un resumen ejecutivo de ventas',
        snapshot=snapshot,
    )
    assert 'concentracion' in answer
    prompt = llm.generate.call_args.args[0]
    assert 'analista empresarial senior' in prompt
    assert 'SNAPSHOT EMPRESARIAL' in prompt
    assert 'largest_customer_share' in prompt

def test_generate_memory_analysis_builds_historian_prompt() -> None:
    llm = MagicMock()
    llm.generate.return_value = 'Respecto al snapshot anterior, el numero de clientes permanece estable.'
    service = AIResponseService(llm)
    answer = service.generate_memory_analysis(
        question='¿Qué ha cambiado?',
        memory_context={
            'latest_snapshot': {'total_customers': 100},
            'previous_snapshot': {'total_customers': 100},
            'memory_insights': {'changes': [], 'stable_findings': ['Estable'], 'new_findings': []},
        },
    )
    assert 'permanece estable' in answer
    prompt = llm.generate.call_args.args[0]
    assert 'historiador empresarial' in prompt
    assert 'memory_insights' in prompt
