"""
Pruebas del orquestador de chat empresarial.
"""

from decimal import Decimal
from unittest.mock import MagicMock

from app.domain.analytics import ClienteVentas, TotalVentasMes
from app.domain.chat import QuestionCategory
from app.services.analytics_service import AnalyticsService
from app.services.chat_orchestrator_service import ChatOrchestratorService


def test_answer_ventas_queries_postgresql() -> None:
    """Verifica que preguntas de ventas consultan analytics (PostgreSQL)."""
    analytics = MagicMock(spec=AnalyticsService)
    analytics.total_ventas_mes.return_value = TotalVentasMes(
        year=2025,
        month=6,
        total=Decimal("125000.00"),
        cantidad_ventas=42,
    )
    llm = MagicMock()

    service = ChatOrchestratorService(analytics, llm)
    answer = service.answer("¿Cuáles fueron las ventas del mes?")

    assert "125,000.00" in answer
    assert "42" in answer
    analytics.total_ventas_mes.assert_called_once()
    llm.generate.assert_not_called()


def test_answer_clientes_queries_postgresql() -> None:
    """Verifica que preguntas de clientes consultan analytics (PostgreSQL)."""
    analytics = MagicMock(spec=AnalyticsService)
    analytics.count_clientes.return_value = 230
    llm = MagicMock()

    service = ChatOrchestratorService(analytics, llm)
    answer = service.answer("¿Cuántos clientes tenemos?")

    assert "230" in answer
    analytics.count_clientes.assert_called_once()
    llm.generate.assert_not_called()


def test_answer_clientes_top_queries_postgresql() -> None:
    """Verifica consulta de top clientes en PostgreSQL."""
    analytics = MagicMock(spec=AnalyticsService)
    analytics.top_clientes.return_value = [
        ClienteVentas("C001", "Alpha Corp", Decimal("5000"), 3),
    ]
    llm = MagicMock()

    service = ChatOrchestratorService(analytics, llm)
    answer = service.answer("¿Cuáles son los mejores clientes?")

    assert "Alpha Corp" in answer
    analytics.top_clientes.assert_called_once_with(limit=5)
    llm.generate.assert_not_called()


def test_answer_general_queries_llm() -> None:
    """Verifica que preguntas generales consultan el LLM."""
    analytics = MagicMock(spec=AnalyticsService)
    llm = MagicMock()
    llm.generate.return_value = "Un ERP es un sistema de planificación de recursos."

    service = ChatOrchestratorService(analytics, llm)
    answer = service.answer("¿Qué es un ERP?")

    assert "ERP" in answer
    llm.generate.assert_called_once()
    analytics.total_ventas_mes.assert_not_called()


def test_classify_exposes_category() -> None:
    """Verifica acceso directo a la categoría clasificada."""
    service = ChatOrchestratorService(MagicMock(), MagicMock())
    assert service.classify("¿Ventas del mes?") == QuestionCategory.VENTAS
