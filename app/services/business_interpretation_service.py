"""
Servicio de interpretación empresarial mediante LLM.

Transforma indicadores de negocio en un prompt estructurado
y obtiene una interpretación neutral del modelo.
"""

from app.integrations.ollama.protocols import LLMClient
from app.services.prompts.business_summary import build_business_summary_prompt


class BusinessInterpretationService:
    """
    Interpreta indicadores empresariales usando Ollama.

    No recomienda acciones ni toma decisiones; delega al LLM
    bajo reglas estrictas de solo interpretación y resumen.
    """

    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client

    def generate_summary(self, ventas_mes: float, clientes: int) -> str:
        """
        Genera una interpretación empresarial a partir de indicadores clave.

        Args:
            ventas_mes: Monto total de ventas del mes.
            clientes: Cantidad total de clientes.

        Returns:
            Texto interpretativo generado por el modelo.
        """
        prompt = build_business_summary_prompt(ventas_mes, clientes)
        return self._llm_client.generate(prompt)

    @staticmethod
    def build_prompt(ventas_mes: float, clientes: int) -> str:
        """
        Expone la construcción del prompt para pruebas y trazabilidad.

        Args:
            ventas_mes: Monto total de ventas del mes.
            clientes: Cantidad total de clientes.

        Returns:
            Prompt estructurado sin ejecutar inferencia.
        """
        return build_business_summary_prompt(ventas_mes, clientes)
