"""
Excepciones del cliente Dynamics 365 F&O.
"""


class DynamicsError(Exception):
    """Excepción base para errores de integración con Dynamics 365."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class DynamicsAuthError(DynamicsError):
    """Error al obtener o validar el token OAuth."""


class DynamicsConnectionError(DynamicsError):
    """Error de red o timeout al comunicarse con Dynamics 365."""


class DynamicsODataError(DynamicsError):
    """Error en la respuesta OData de Dynamics 365."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)
