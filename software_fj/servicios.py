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
    def calcular_costo_base(self, horas, **parametros) -> float:
        """Costo sin impuestos ni descuentos. Cada servicio lo calcula distinto."""
        raise NotImplementedError  # Cada servicio hijo debe implementarlo

    @abstractmethod
    def validar_parametros(self, horas, **parametros) -> bool:
        """Valida los parámetros propios del servicio. Lanza excepción si fallan."""
        raise NotImplementedError  # Cada servicio hijo debe implementarlo

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
    
    
    
    

# ===========================================================================
# Servicio 1: Reserva de salas
# ===========================================================================
class ReservaSala(Servicio):
    """Alquiler de salas de reuniones o capacitación."""

    RECARGO_GRUPO_GRANDE = 0.10      # +10 % si asisten más de 20 personas

    def __init__(self, codigo, nombre, tarifa_hora, capacidad, disponible=True):
        super().__init__(codigo, nombre, tarifa_hora, disponible)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ValidacionError("capacidad", "debe ser un entero positivo")
        self.capacidad = capacidad

    def validar_parametros(self, horas, **parametros):
        personas = parametros.get("personas")
        if personas is None:
            raise ParametroFaltanteError("personas")
        if not 1 <= horas <= 12:
            raise ValidacionError("horas", "una sala se reserva entre 1 y 12 horas")
        if personas > self.capacidad:
            raise ValidacionError(
                "personas", f"{personas} superan la capacidad de la sala ({self.capacidad})"
            )
        return True

    def calcular_costo_base(self, horas, **parametros):
        base = self.tarifa_hora * horas
        if parametros.get("personas", 0) > 20:          # Recargo por grupo grande
            base *= 1 + self.RECARGO_GRUPO_GRANDE
        return base

    def describir(self):
        return (f"Sala '{self.nombre}' ({self.codigo}) - capacidad {self.capacidad} "
                f"personas - ${self.tarifa_hora:,.0f}/hora")


# ===========================================================================
# Servicio 2: Alquiler de equipos
# ===========================================================================
class AlquilerEquipo(Servicio):
    """Alquiler de equipos (portátiles, proyectores, etc.)."""

    DEPOSITO_POR_UNIDAD = 20000      # Depósito fijo por cada equipo alquilado

    def __init__(self, codigo, nombre, tarifa_hora, unidades_disponibles, disponible=True):
        super().__init__(codigo, nombre, tarifa_hora, disponible)
        if not isinstance(unidades_disponibles, int) or unidades_disponibles < 0:
            raise ValidacionError("unidades_disponibles", "debe ser un entero >= 0")
        self.unidades_disponibles = unidades_disponibles

    def validar_parametros(self, horas, **parametros):
        cantidad = parametros.get("cantidad")
        if cantidad is None:
            raise ParametroFaltanteError("cantidad")
        if cantidad <= 0:
            raise ValidacionError("cantidad", "debe alquilar al menos un equipo")
        if not 1 <= horas <= 72:
            raise ValidacionError("horas", "un equipo se alquila entre 1 y 72 horas")
        if cantidad > self.unidades_disponibles:
            raise ValidacionError(
                "cantidad",
                f"solo hay {self.unidades_disponibles} unidades de '{self.nombre}'",
            )
        return True

    def calcular_costo_base(self, horas, **parametros):
        cantidad = parametros.get("cantidad", 1)
        return self.tarifa_hora * horas * cantidad + self.DEPOSITO_POR_UNIDAD * cantidad

    def describir(self):
        return (f"Equipo '{self.nombre}' ({self.codigo}) - {self.unidades_disponibles} "
                f"unidades - ${self.tarifa_hora:,.0f}/hora")


# ===========================================================================
# Servicio 3: Asesorías especializadas
# ===========================================================================
class Asesoria(Servicio):
    """Asesoría con un especialista; el nivel cambia la tarifa."""

    MULTIPLICADOR_NIVEL = {"basico": 1.0, "avanzado": 1.5, "experto": 2.0}

    def __init__(self, codigo, nombre, tarifa_hora, especialidad, disponible=True):
        super().__init__(codigo, nombre, tarifa_hora, disponible)
        if not especialidad:
            raise ParametroFaltanteError("especialidad")
        self.especialidad = especialidad

    def validar_parametros(self, horas, **parametros):
        nivel = parametros.get("nivel", "basico")
        if nivel not in self.MULTIPLICADOR_NIVEL:
            raise ValidacionError(
                "nivel", f"'{nivel}' no existe; use {list(self.MULTIPLICADOR_NIVEL)}"
            )
        if not 1 <= horas <= 8:
            raise ValidacionError("horas", "una asesoría dura entre 1 y 8 horas")
        return True

    def calcular_costo_base(self, horas, **parametros):
        nivel = parametros.get("nivel", "basico")
        return self.tarifa_hora * horas * self.MULTIPLICADOR_NIVEL[nivel]

    def describir(self):
        return (f"Asesoría '{self.nombre}' ({self.codigo}) en {self.especialidad} "
                f"- ${self.tarifa_hora:,.0f}/hora")