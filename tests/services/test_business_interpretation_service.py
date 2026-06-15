"""
Pruebas del servicio de interpretación empresarial.
"""

from unittest.mock import MagicMock

from app.services.business_interpretation_service import BusinessInterpretationService


def test_generate_summary_builds_prompt_and_calls_llm() -> None:
    """Verifica construcción de prompt y delegación al cliente LLM."""
    llm_client = MagicMock()
    llm_client.generate.return_value = "Resumen interpretativo neutral."

    service = BusinessInterpretationService(llm_client)
    result = service.generate_summary(ventas_mes=125000, clientes=230)

    assert result == "Resumen interpretativo neutral."
    llm_client.generate.assert_called_once()
    prompt = llm_client.generate.call_args[0][0]
    assert "125,000.00" in prompt
    assert "230" in prompt
    assert "NO recomiendes" in prompt


def test_build_prompt_exposes_prompt_without_inference() -> None:
    """Verifica acceso al prompt estructurado sin llamar al LLM."""
    prompt = BusinessInterpretationService.build_prompt(ventas_mes=50000, clientes=100)

    assert "50,000.00" in prompt
    assert "100" in prompt
