"""
Prompt estructurado para interpretación empresarial.

Genera instrucciones para el LLM con reglas estrictas:
solo interpretar y resumir, sin recomendar ni decidir.
"""


def build_business_summary_prompt(ventas_mes: float, clientes: int) -> str:
    """
    Construye el prompt estructurado para interpretar indicadores empresariales.

    Args:
        ventas_mes: Monto total de ventas del mes.
        clientes: Cantidad total de clientes.

    Returns:
        Prompt listo para enviar al modelo de lenguaje.
    """
    ventas_formateadas = f"{ventas_mes:,.2f}"

    return f"""Eres un analista empresarial. Tu tarea es interpretar y resumir los siguientes indicadores de negocio.

DATOS:
- Ventas del mes: {ventas_formateadas}
- Total de clientes: {clientes}

REGLAS ESTRICTAS:
- NO recomiendes acciones, estrategias ni próximos pasos.
- NO tomes decisiones ni emitas juicios prescriptivos.
- NO uses frases como "debería", "conviene", "se recomienda" o "es necesario".
- SOLO interpreta los datos y resume su significado de forma neutral y descriptiva.

FORMATO DE RESPUESTA:
- Redacta en español.
- Usa un párrafo breve (3 a 5 oraciones).
- Describe qué indican los números sin proponer cambios ni conclusiones operativas.

Interpreta y resume los indicadores:"""
