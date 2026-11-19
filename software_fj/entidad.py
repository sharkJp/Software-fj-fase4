"""
entidad.py
Clase abstracta que representa cualquier entidad general del sistema
(clientes, servicios y reservas heredan de ella).
"""

from abc import ABC, abstractmethod   # Herramientas para clases abstractas
from datetime import datetime          # Para registrar la fecha de creación
import itertools                       # Para generar identificadores únicos


class Entidad(ABC):
    """Entidad base abstracta: no se puede instanciar directamente."""

    # Un contador por cada tipo de entidad (Cliente, Reserva, ...) para IDs únicos
    _contadores = {}

    def __init__(self):
        # Nombre de la clase hija que se está creando, ej. "Cliente"
        tipo = type(self).__name__
        # Si ese tipo aún no tiene contador, se le crea uno que empieza en 1
        contador = Entidad._contadores.setdefault(tipo, itertools.count(1))
        # Identificador único e inmutable (atributo "privado" con doble guion)
        self.__id = next(contador)
        # Momento exacto en que se creó el objeto
        self.__fecha_creacion = datetime.now()

    @property
    def id(self):
        """ID único de la entidad (solo lectura)."""
        return self.__id

    @property
    def fecha_creacion(self):
        """Fecha de creación (solo lectura)."""
        return self.__fecha_creacion

    @abstractmethod
    def validar(self):
        """Cada entidad define sus propias reglas de validación.
        Debe lanzar una excepción si algo no es válido."""

    @abstractmethod
    def describir(self):
        """Cada entidad devuelve una descripción legible de sí misma."""

    def __str__(self):
        # Por defecto, mostrar una entidad es mostrar su descripción
        return self.describir()