"""
Factory del cliente Dynamics 365 F&O.

Centraliza la construcción del cliente a partir de Settings,
facilitando inyección de dependencias y pruebas.
"""

from app.core.config import Settings, settings
from app.integrations.dynamics.oauth import AzureADOAuthProvider, OAuthConfig
from app.integrations.dynamics.odata_client import DynamicsODataClient, ODataClientConfig


def build_oauth_config(app_settings: Settings) -> OAuthConfig:
    """Construye la configuración OAuth desde Settings."""
    return OAuthConfig(
        tenant_id=app_settings.D365_TENANT_ID,
        client_id=app_settings.D365_CLIENT_ID,
        client_secret=app_settings.D365_CLIENT_SECRET,
        scope=app_settings.d365_oauth_scope,
        token_url=app_settings.d365_token_url,
        timeout=app_settings.D365_REQUEST_TIMEOUT,
    )


def build_odata_config(app_settings: Settings) -> ODataClientConfig:
    """Construye la configuración OData desde Settings."""
    return ODataClientConfig(
        base_url=app_settings.D365_BASE_URL,
        health_entity=app_settings.D365_HEALTH_ENTITY,
        timeout=app_settings.D365_REQUEST_TIMEOUT,
    )


def create_dynamics_client(
    app_settings: Settings | None = None,
) -> DynamicsODataClient:
    """
    Crea una instancia del cliente OData de Dynamics 365 F&O.

    Args:
        app_settings: Configuración de la aplicación. Usa settings global si es None.

    Returns:
        Cliente OData listo para consultar entidades.
    """
    config = app_settings or settings
    oauth_provider = AzureADOAuthProvider(build_oauth_config(config))
    return DynamicsODataClient(
        config=build_odata_config(config),
        oauth_provider=oauth_provider,
    )
