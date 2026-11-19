"""
servicios.py
Clase abstracta Servicio y tres servicios especializados:
    - ReservaSala
    - AlquilerEquipo
    - Asesoria

Demuestra herencia, polimorfismo (cada servicio calcula, describe y valida
a su manera) y sobrecarga del método calcular_costo.
"""

from abc import abstractmethod          # Para declarar métodos abstractos
from typing import overload             # Para declarar formalmente la sobrecarga
from .entidad import Entidad
from .excepciones import (
    ValidacionError,
    ParametroFaltanteError,
    ServicioNoDisponibleError,
    CalculoError,
)

IVA = 0.19          # Impuesto por defecto en Colombia (19 %)


class Servicio(Entidad):
    """Servicio genérico de Software FJ (clase abstracta)."""

    def __init__(self, codigo, nombre, tarifa_hora, disponible=True):
        super().__init__()
        # Validaciones comunes a todos los servicios
        if not codigo:
            raise ParametroFaltanteError("codigo")
        if not nombre:
            raise ParametroFaltanteError("nombre")
        if not isinstance(tarifa_hora, (int, float)) or tarifa_hora <= 0:
            raise ValidacionError("tarifa_hora", "debe ser un número mayor que cero")
        self.__codigo = str(codigo).upper()     # Código único, en mayúsculas
        self.__nombre = nombre                   # Nombre comercial
        self.__tarifa_hora = float(tarifa_hora)  # Precio por hora
        self.__disponible = bool(disponible)     # ¿Se puede reservar?

    # ------------------------- propiedades --------------------------------
    @property
    def codigo(self):
        return self.__codigo

    @property
    def nombre(self):
        return self.__nombre

    @property
    def tarifa_hora(self):
        return self.__tarifa_hora

    @property
    def disponible(self):
        return self.__disponible

    def activar(self):
        """Marca el servicio como disponible."""
        self.__disponible = True

    def desactivar(self):
        """Marca el servicio como no disponible (mantenimiento, agotado...)."""
        self.__disponible = False

    def verificar_disponibilidad(self):
        """Lanza ServicioNoDisponibleError si el servicio está inactivo."""
        if not self.__disponible:
            raise ServicioNoDisponibleError(self.__nombre)
        return True

    # ------------------- métodos que cada hijo sobrescribe ----------------
    @abstractmethod
    def calcular_costo_base(self, horas, **parametros):
        """Costo sin impuestos ni descuentos. Cada servicio lo calcula distinto."""

    @abstractmethod
    def validar_parametros(self, horas, **parametros):
        """Valida los parámetros propios del servicio. Lanza excepción si fallan."""

    def validar(self):
        """Validación general de la entidad servicio."""
        return self.tarifa_hora > 0 and bool(self.codigo)

    # ------------------------- SOBRECARGA ---------------------------------
    # Python no tiene sobrecarga como Java/C#. Se simula con parámetros
    # opcionales; los decoradores @overload documentan las variantes válidas:
    @overload
    def calcular_costo(self, horas: float) -> float: ...
    @overload
    def calcular_costo(self, horas: float, impuesto: float) -> float: ...
    @overload
    def calcular_costo(self, horas: float, impuesto: float, descuento: float) -> float: ...

    def calcular_costo(self, horas, impuesto=None, descuento=0.0, **parametros):
        """
        Variantes de uso (sobrecarga):
            calcular_costo(horas)                       -> base + IVA por defecto
            calcular_costo(horas, impuesto)             -> base + impuesto indicado
            calcular_costo(horas, impuesto, descuento)  -> con impuesto y descuento
        Los **parametros extra se pasan al cálculo base (ej. personas, cantidad).
        """
        impuesto = IVA if impuesto is None else impuesto   # Valor por defecto
        # Validamos rangos de impuesto y descuento
        if not 0 <= impuesto <= 1:
            raise CalculoError(f"Impuesto fuera de rango: {impuesto}")
        if not 0 <= descuento < 1:
            raise CalculoError(f"Descuento fuera de rango: {descuento}")

        base = self.calcular_costo_base(horas, **parametros)   # Polimorfismo
        total = base * (1 - descuento) * (1 + impuesto)         # Fórmula final

        # Verificación de consistencia: un costo nunca puede ser negativo o cero
        if total <= 0:
            raise CalculoError(f"Costo inconsistente calculado: {total}")
        return round(total, 2)

    def __str__(self):
        estado = "Disponible" if self.disponible else "NO disponible"
        return f"{self.describir()} [{estado}]"