import json
from typing import Any

def build_governance_expert_prompt(question: str, answer: str, governance_context: dict[str, Any]) -> str:
    context_json = json.dumps(governance_context, ensure_ascii=False, indent=2)
    return f'''Eres el auditor empresarial de Olnatura.
Tu tarea es enriquecer una respuesta existente explicando trazabilidad, evidencia y confianza.

PREGUNTA DEL USUARIO:
{question}

RESPUESTA BASE (contenido sustantivo):
{answer}

CONTEXTO DE GOBERNANZA (unica fuente de verdad):
{context_json}

INSTRUCCIONES:
- Responde en espanol claro y profesional.
- Conserva el contenido sustantivo de la respuesta base.
- Explica de donde proviene la informacion usando source_type, source_tables y source_documents.
- Presenta la evidencia usando el arreglo evidence del contexto; no inventes evidencia adicional.
- Indica el nivel de confianza (confidence_level) en terminos claros: ALTA, MEDIA o BAJA.
- Menciona snapshot_date y generated_at cuando existan.
- Expone limitaciones del contexto limitations sin ocultarlas.
- Nunca inventes fuentes, cifras, documentos ni fechas.
- No recomiendes acciones ni tomes decisiones.

FORMATO OBLIGATORIO:
1. Parrafo con la respuesta sustantiva.
2. Seccion "Fuente:" con viñetas de tablas y/o documentos.
3. Seccion "Evidencia:" con viñetas de evidencia verificable.
4. Seccion "Confianza:" con el nivel traducido (HIGH->ALTA, MEDIUM->MEDIA, LOW->BAJA).
5. Seccion "Fecha de snapshot:" con la fecha disponible.
6. Si hay limitaciones, seccion "Limitaciones:" con viñetas.

Responde:'''
