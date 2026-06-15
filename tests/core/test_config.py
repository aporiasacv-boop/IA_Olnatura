"""
Pruebas de la configuración centralizada Settings.
"""

from app.core.config import Settings, get_settings


def test_settings_loads_defaults() -> None:
    """Verifica que Settings expone valores por defecto válidos."""
    config = Settings()

    assert config.APP_NAME == "Asistente de Inteligencia Empresarial Olnatura"
    assert config.APP_VERSION == "0.1.0"
    assert config.LOG_LEVEL == "INFO"
    assert config.HOST == "0.0.0.0"
    assert config.PORT == 8000


def test_get_settings_returns_singleton() -> None:
    """Verifica que get_settings retorna la misma instancia cacheada."""
    get_settings.cache_clear()
    first = get_settings()
    second = get_settings()
    assert first is second
    get_settings.cache_clear()


def test_d365_oauth_scope_is_derived_from_base_url() -> None:
    """Verifica derivación automática del scope OAuth."""
    config = Settings(
        D365_BASE_URL="https://prod.operations.dynamics.com/data",
        D365_OAUTH_SCOPE="",
    )
    assert config.d365_oauth_scope == "https://prod.operations.dynamics.com/.default"


def test_d365_token_url_is_derived_from_tenant_id() -> None:
    """Verifica derivación automática de la URL del token OAuth."""
    config = Settings(
        D365_TENANT_ID="abc-123",
        D365_TOKEN_URL="",
    )
    assert (
        config.d365_token_url
        == "https://login.microsoftonline.com/abc-123/oauth2/v2.0/token"
    )
