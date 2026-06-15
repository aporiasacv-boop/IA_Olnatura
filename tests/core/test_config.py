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
