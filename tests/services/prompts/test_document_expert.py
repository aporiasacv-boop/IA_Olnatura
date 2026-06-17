from app.services.prompts.document_expert import build_document_expert_prompt

def test_build_document_expert_prompt_includes_context_and_rules() -> None:
    document_context = {
        'documents': [{'document_name': 'Manual.pdf', 'score': 0.91, 'content': 'Contenido'}],
        'sources': ['Manual.pdf'],
        'top_document': 'Manual.pdf',
        'total_matches': 1,
        'average_score': 0.91,
        'context': '[Manual.pdf] contenido',
    }
    document_insights = {
        'confidence_level': 'HIGH',
        'source_documents': ['Manual.pdf'],
        'top_document': 'Manual.pdf',
        'total_matches': 1,
        'average_score': 0.91,
    }
    prompt = build_document_expert_prompt(
        question='¿Qué hace el analista de procesos?',
        document_context=document_context,
        document_insights=document_insights,
    )
    assert 'especialista documental corporativo' in prompt
    assert 'CONTEXTO DOCUMENTAL' in prompt
    assert 'INSIGHTS DOCUMENTALES' in prompt
    assert 'confidence_level' in prompt
    assert 'No recomiendes acciones' in prompt
    assert '¿Qué hace el analista de procesos?' in prompt
