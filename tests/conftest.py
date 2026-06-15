"""
Fixtures compartidas de pytest.

Configura el cliente de pruebas y recursos reutilizables
para todos los módulos de test del proyecto.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """
    Cliente HTTP de prueba contra la aplicación FastAPI.

    No levanta un servidor real; invoca la app directamente en memoria.
    """
    with TestClient(app) as test_client:
        yield test_client
