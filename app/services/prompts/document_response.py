import json
from typing import Any

def build_document_response_prompt(question: str, results: list[dict[str, Any]]) -> str:
    context_json = json.dumps(results, ensure_ascii=False, indent=2)
    return f'Eres un asistente de inteligencia empresarial de Olnatura.\nTu tarea es responder la pregunta del usuario usando unicamente los fragmentos documentales recuperados.\n\nPREGUNTA DEL USUARIO:\n{question}\n\nFRAGMENTOS DOCUMENTALES (unica fuente de verdad):\n{context_json}\n\nREGLAS ESTRICTAS:\n- Usa UNICAMENTE los fragmentos proporcionados.\n- NO consultes bases de datos, SQL, Dynamics ni sistemas externos.\n- NO inventes informacion que no este en los fragmentos.\n- NO recomiendes acciones, estrategias ni proximos pasos.\n- NO uses frases como "deberia", "conviene", "se recomienda" o "es necesario".\n- SOLO interpreta el contenido documental en lenguaje natural en espanol.\n- Si los fragmentos no contienen informacion suficiente, indicalo de forma clara.\n\nFORMATO DE RESPUESTA:\n- Redacta en espanol.\n- Usa un parrafo breve y claro.\n\nResponde:'
