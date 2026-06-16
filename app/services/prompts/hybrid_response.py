import json
from typing import Any
from app.services.context_fusion_service import FusedContext

def build_hybrid_response_prompt(question: str, context: FusedContext) -> str:
    payload = {
        'analytics': {
            'intent': context.analytics_intent,
            'data': context.analytics_data,
        },
        'documents': context.document_results,
    }
    context_json = json.dumps(payload, ensure_ascii=False, indent=2)
    return f'Eres un asistente de inteligencia empresarial de Olnatura.\nTu tarea es responder la pregunta del usuario combinando datos analiticos y fragmentos documentales.\n\nPREGUNTA DEL USUARIO:\n{question}\n\nCONTEXTO FUSIONADO (unica fuente de verdad):\n{context_json}\n\nREGLAS ESTRICTAS:\n- Usa UNICAMENTE el contexto fusionado proporcionado.\n- Integra datos analiticos y documentales en una respuesta coherente.\n- NO consultes bases de datos, SQL, Dynamics ni sistemas externos.\n- NO inventes cifras, clientes, pedidos ni procedimientos.\n- NO recomiendes acciones, estrategias ni proximos pasos.\n- NO uses frases como "deberia", "conviene", "se recomienda" o "es necesario".\n- SOLO interpreta el contexto en lenguaje natural en espanol.\n- Si una parte del contexto no contiene informacion suficiente, indicalo de forma clara.\n- Menciona que los datos analiticos provienen de Dynamics 365 Finance & Operations cuando sea relevante.\n\nFORMATO DE RESPUESTA:\n- Redacta en espanol.\n- Usa uno o dos parrafos breves y claros.\n- Responde todas las partes de la pregunta en una sola respuesta unificada.\n\nResponde:'
