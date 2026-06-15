"""
Prompt RAG para consultas sobre documentos indexados.
"""

RAG_QUERY_PROMPT = """Eres un asistente empresarial. Responde la pregunta usando ÚNICAMENTE el contexto proporcionado.
Si el contexto no contiene información suficiente, indícalo claramente.
Responde en español de forma clara y concisa.
NO inventes información que no esté en el contexto.

CONTEXTO:
{context}

PREGUNTA:
{question}

RESPUESTA:"""


def build_rag_prompt(context: str, question: str) -> str:
    """Construye el prompt RAG con contexto recuperado."""
    return RAG_QUERY_PROMPT.format(context=context.strip(), question=question.strip())
