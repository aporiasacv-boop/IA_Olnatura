"""
Servicio de verificación de conectividad con Dynamics 365 F&O.
"""

from app.integrations.dynamics.exceptions import DynamicsError
from app.integrations.dynamics.protocols import DynamicsClient


class DynamicsHealthService:
    """Encapsula la lógica de health check OData contra Dynamics 365."""

    def __init__(self, client: DynamicsClient):
        self._client = client

    def is_connected(self) -> bool:
        """
        Verifica conectividad consultando la entidad de prueba configurada.

        Returns:
            True si Dynamics responde correctamente; False en caso de error.
        """
        try:
            self._client.ping()
            return True
        except DynamicsError:
            return False
