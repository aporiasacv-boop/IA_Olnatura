"""
Excepciones personalizadas del dominio y capa de aplicación.

Centralizar excepciones permite manejo uniforme en la capa API
y respuestas HTTP consistentes para el cliente.
"""


class AppException(Exception):
    """Excepción base de la aplicación."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(AppException):
    """Recurso solicitado no encontrado (HTTP 404)."""

    def __init__(self, message: str = "Recurso no encontrado"):
        super().__init__(message=message, status_code=404)


class ValidationException(AppException):
    """Error de validación de reglas de negocio (HTTP 422)."""

    def __init__(self, message: str = "Error de validación"):
        super().__init__(message=message, status_code=422)
