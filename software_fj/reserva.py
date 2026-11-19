"""
reserva.py
Clase Reserva: integra cliente, servicio, duración y estado.
Implementa confirmación, cancelación y procesamiento con manejo de excepciones.
"""

from enum import Enum                    # Para definir los estados posibles
from .entidad import Entidad
from .cliente import Cliente
from .servicios import Servicio
from .registro import obtener_logger
from .excepciones import (
    ReservaInvalidaError,
    OperacionNoPermitidaError,
    CalculoError,
    SoftwareFJError,
)

log = obtener_logger("software_fj.reserva")   # Logger propio de este módulo


class EstadoReserva(Enum):
    """Estados por los que puede pasar una reserva."""
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    PROCESADA = "Procesada"
    CANCELADA = "Cancelada"


class Reserva(Entidad):
    """Reserva de un servicio por parte de un cliente."""

    def __init__(self, cliente, servicio, horas, **parametros):
        # --- Validación de tipos: deben ser objetos del dominio -------------
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un objeto Cliente válido")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un objeto Servicio válido")

        # --- Conversión de horas con ENCADENAMIENTO de excepciones ----------
        try:
            horas = float(horas)                 # Puede lanzar ValueError/TypeError
        except (ValueError, TypeError) as error:
            # 'raise ... from error' conserva el error original como causa
            raise ReservaInvalidaError(f"Duración inválida: {horas!r}") from error

        if horas <= 0:
            raise ReservaInvalidaError("La duración debe ser mayor que cero")

        # --- Reglas del servicio (polimorfismo: cada servicio valida a su modo)
        servicio.verificar_disponibilidad()               # ¿Está activo?
        servicio.validar_parametros(horas, **parametros)  # ¿Parámetros correctos?

        # Solo si todo es válido se asigna el ID (así no se "gastan" IDs en intentos fallidos)
        super().__init__()
        self.__cliente = cliente
        self.__servicio = servicio
        self.__horas = horas
        self.__parametros = parametros           # personas, cantidad, nivel...
        self.__estado = EstadoReserva.PENDIENTE  # Toda reserva nace pendiente
        self.__costo = None                      # Se conoce al procesarla

    # ------------------------- propiedades --------------------------------
    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def horas(self):
        return self.__horas

    @property
    def estado(self):
        return self.__estado

    @property
    def costo(self):
        return self.__costo

    # ------------------------- operaciones --------------------------------
    def confirmar(self):
        """Pasa la reserva de PENDIENTE a CONFIRMADA."""
        if self.__estado != EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar la reserva #{self.id}: está {self.__estado.value}"
            )
        self.__estado = EstadoReserva.CONFIRMADA
        log.info("Reserva #%s confirmada", self.id)

    def cancelar(self, motivo="Sin motivo"):
        """Cancela la reserva si aún no ha sido procesada."""
        if self.__estado in (EstadoReserva.PROCESADA, EstadoReserva.CANCELADA):
            raise OperacionNoPermitidaError(
                f"No se puede cancelar la reserva #{self.id}: está {self.__estado.value}"
            )
        self.__estado = EstadoReserva.CANCELADA
        log.info("Reserva #%s cancelada. Motivo: %s", self.id, motivo)

    def procesar(self, impuesto=None, descuento=0.0):
        """
        Calcula el costo final y marca la reserva como PROCESADA.
        Usa TRY / EXCEPT / ELSE / FINALLY y encadenamiento de excepciones.
        """
        if self.__estado != EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitidaError(
                f"Solo se procesan reservas confirmadas (#{self.id} está {self.__estado.value})"
            )
        try:
            # Llamada polimórfica: el servicio concreto sabe cómo calcular su costo
            costo = self.__servicio.calcular_costo(
                self.__horas, impuesto, descuento, **self.__parametros
            )
        except CalculoError:
            # Error de cálculo propio: se registra y se propaga tal cual
            log.error("Cálculo inconsistente en reserva #%s", self.id)
            raise
        except (TypeError, ValueError, KeyError) as error:
            # Error inesperado de Python: se ENCADENA en una excepción del dominio
            raise CalculoError(
                f"Fallo inesperado al calcular la reserva #{self.id}"
            ) from error
        else:
            # ELSE: solo se ejecuta si NO hubo excepción
            self.__costo = costo
            self.__estado = EstadoReserva.PROCESADA
            log.info("Reserva #%s procesada. Total: $%s", self.id, f"{costo:,.2f}")
            return costo
        finally:
            # FINALLY: se ejecuta SIEMPRE, haya o no error (auditoría)
            log.debug("Intento de procesamiento de la reserva #%s finalizado", self.id)

    # ------------------------ métodos abstractos ---------------------------
    def validar(self):
        try:
            self.__servicio.validar_parametros(self.__horas, **self.__parametros)
        except SoftwareFJError as error:
            raise ReservaInvalidaError(f"La reserva #{self.id} ya no es válida") from error
        return True

    def describir(self):
        costo = f"${self.__costo:,.2f}" if self.__costo is not None else "por calcular"
        return (f"Reserva #{self.id}: {self.__cliente.nombre} -> {self.__servicio.nombre} "
                f"| {self.__horas:g} h | {self.__estado.value} | {costo}")