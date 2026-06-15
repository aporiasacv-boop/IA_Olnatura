"""
Servicio base.

Clase abstracta de la que heredarán los servicios concretos del dominio.
Centraliza la inyección de repositorios y utilidades compartidas.
"""

from sqlalchemy.orm import Session


class BaseService:
    """
    Servicio base con acceso a la sesión de base de datos.

    Los servicios concretos recibirán repositorios especializados
    y encapsularán la lógica de negocio del sistema.
    """

    def __init__(self, db: Session):
        self.db = db

    # La lógica de negocio específica se implementará en servicios derivados.
