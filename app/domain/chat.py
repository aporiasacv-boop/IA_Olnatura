"""
Dominio del orquestador de chat empresarial.
"""

from enum import Enum


class QuestionCategory(str, Enum):
    """Categoría identificada para una pregunta empresarial."""

    VENTAS = "ventas"
    CLIENTES = "clientes"
    GENERAL = "general"
