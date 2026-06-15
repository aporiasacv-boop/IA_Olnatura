"""
Pruebas del endpoint POST /chat.
"""

from decimal import Decimal
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.deps import get_chat_orchestrator_service
from app.integrations.ollama.exceptions import OllamaConnectionError
from app.main import app
from app.repositories.analytics_repository import AnalyticsRepository
from app.services.analytics_service import AnalyticsService
from app.services.chat_orchestrator_service import ChatOrchestratorService


def test_post_chat_ventas_with_real_analytics(analytics_db: Session) -> None:
    """Verifica respuesta de ventas con analytics real en SQLite."""
    from datetime import date
    from decimal import Decimal

    from app.models.venta import Venta

    today = date.today()
    analytics_db.add(
        Venta(
            dynamics_id="SO-CHAT",
            cliente_dynamics_id="C001",
            monto=Decimal("125000.00"),
            fecha=date(today.year, today.month, 10),
            estado="Open",
        )
    )
    analytics_db.commit()

    analytics_service = AnalyticsService(AnalyticsRepository(analytics_db))
    llm = MagicMock()

    def override_service() -> ChatOrchestratorService:
        return ChatOrchestratorService(analytics_service, llm)

    app.dependency_overrides[get_chat_orchestrator_service] = override_service
    try:
        with TestClient(app) as client:
            response = client.post(
                "/chat",
                json={"question": "¿Cuáles fueron las ventas del mes?"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "answer" in response.json()
    assert "125,000.00" in response.json()["answer"]
    llm.generate.assert_not_called()


def test_post_chat_general_with_mocked_llm() -> None:
    """Verifica que preguntas generales usan el LLM."""
    mock_service = MagicMock(spec=ChatOrchestratorService)
    mock_service.answer.return_value = "Un ERP integra procesos empresariales."

    app.dependency_overrides[get_chat_orchestrator_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.post(
                "/chat",
                json={"question": "¿Qué es un ERP?"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["answer"] == "Un ERP integra procesos empresariales."
    mock_service.answer.assert_called_once_with("¿Qué es un ERP?")


def test_post_chat_returns_503_on_llm_error() -> None:
    """Verifica HTTP 503 cuando el LLM falla en preguntas generales."""
    mock_service = MagicMock(spec=ChatOrchestratorService)
    mock_service.answer.side_effect = OllamaConnectionError("No se pudo conectar con Ollama")

    app.dependency_overrides[get_chat_orchestrator_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.post(
                "/chat",
                json={"question": "¿Qué es un ERP?"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503


def test_post_chat_validates_empty_question() -> None:
    """Verifica validación de pregunta vacía."""
    with TestClient(app) as client:
        response = client.post("/chat", json={"question": ""})

    assert response.status_code == 422
