RAG_QUERY_PROMPT = 'Eres un asistente empresarial. Responde la pregunta usando ÚNICAMENTE el contexto proporcionado.\nSi el contexto no contiene información suficiente, indícalo claramente.\nResponde en español de forma clara y concisa.\nNO inventes información que no esté en el contexto.\n\nCONTEXTO:\n{context}\n\nPREGUNTA:\n{question}\n\nRESPUESTA:'

def build_rag_prompt(context: str, question: str) -> str:
    return RAG_QUERY_PROMPT.format(context=context.strip(), question=question.strip())
