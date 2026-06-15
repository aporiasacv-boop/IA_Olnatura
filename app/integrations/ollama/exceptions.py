"""
Excepciones del cliente Ollama.
"""


class OllamaError(Exception):
    """Excepción base para errores de integración con Ollama."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class OllamaConnectionError(OllamaError):
    """Error de red o timeout al comunicarse con Ollama."""


class OllamaAPIError(OllamaError):
    """Error en la respuesta HTTP de la API Ollama."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)
