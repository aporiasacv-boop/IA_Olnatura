"""
Contratos (protocolos) del cliente Dynamics 365.

Permiten inyectar implementaciones mock en pruebas
sin acoplar servicios al cliente HTTP concreto.
"""

from typing import Any, Protocol


class OAuthTokenProvider(Protocol):
    """Proveedor de tokens de acceso OAuth 2.0."""

    def get_access_token(self) -> str:
        """Obtiene un token Bearer válido para la API OData."""
        ...


class DynamicsClient(Protocol):
    """Contrato mínimo del cliente OData de Dynamics 365 F&O."""

    def ping(self) -> None:
        """
        Verifica conectividad consultando una entidad de prueba.

        Raises:
            DynamicsError: Si la consulta falla.
        """
        ...

    def query_entity(self, entity_name: str, top: int = 1) -> dict[str, Any]:
        """
        Consulta registros de una entidad OData.

        Args:
            entity_name: Nombre de la entidad (ej. Companies).
            top: Cantidad máxima de registros a retornar.

        Returns:
            Respuesta JSON de OData.
        """
        ...

    def fetch_all_entity(self, entity_name: str, page_size: int = 100) -> list[dict[str, Any]]:
        """
        Extrae todos los registros de una entidad con paginación OData.

        Args:
            entity_name: Nombre de la entidad OData.
            page_size: Tamaño de página ($top).

        Returns:
            Lista plana de registros.
        """
        ...
