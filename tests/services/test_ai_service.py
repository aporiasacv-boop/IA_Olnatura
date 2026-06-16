from unittest.mock import MagicMock
from app.services.ai_service import AIService

def test_test_prompt_delegates_to_llm_client() -> None:
    llm_client = MagicMock()
    llm_client.generate.return_value = 'Respuesta del modelo'
    service = AIService(llm_client)
    result = service.test_prompt('Hola')
    assert result == 'Respuesta del modelo'
    llm_client.generate.assert_called_once_with('Hola')
