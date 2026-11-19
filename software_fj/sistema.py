"""
sistema.py
Clase SistemaGestion: administra las listas internas de clientes,
servicios y reservas (sin base de datos) y registra cada evento en el log.
"""

from .cliente import Cliente
from .reserva import Reserva, EstadoReserva
from .registro import obtener_logger
from .excepciones import (
    SoftwareFJError,
    ClienteDuplicadoError,
    ClienteNoEncontradoError,
    ServicioNoEncontradoError,
    ReservaInvalidaError,
    ValidacionError,
)

log = obtener_logger("software_fj.sistema")


class SistemaGestion:
    """Punto central de la aplicación Software FJ."""

    def __init__(self):
        self.__clientes = []      # Lista interna de objetos Cliente
        self.__servicios = []     # Lista interna de objetos Servicio
        self.__reservas = []      # Lista interna de objetos Reserva
        log.info("Sistema Software FJ iniciado")

    # Copias de las listas: desde afuera se pueden leer pero no modificar
    @property
    def clientes(self):
        return list(self.__clientes)

    @property
    def servicios(self):
        return list(self.__servicios)

    @property
    def reservas(self):
        return list(self.__reservas)

    # ============================ CLIENTES ================================
    def registrar_cliente(self, nombre, documento, correo, telefono=None):
        """Crea y guarda un cliente. try/except/else."""
        try:
            # Primero se valida que el documento no esté repetido
            if any(c.documento == str(documento).strip() for c in self.__clientes):
                raise ClienteDuplicadoError(documento)
            cliente = Cliente(nombre, documento, correo, telefono)   # Puede fallar
        except SoftwareFJError as error:
            log.warning("Registro de cliente rechazado: %s", error)
            raise                                  # Se informa a quien llamó
        else:
            self.__clientes.append(cliente)        # Solo si todo salió bien
            log.info("Cliente registrado: %s", cliente.describir())
            return cliente

    def buscar_cliente(self, documento):
        for cliente in self.__clientes:
            if cliente.documento == str(documento):
                return cliente
        raise ClienteNoEncontradoError(documento)

    # ============================ SERVICIOS ===============================
    def agregar_servicio(self, clase_servicio, *args, **kwargs):
        """Crea un servicio de cualquier tipo (polimorfismo por la clase)."""
        try:
            servicio = clase_servicio(*args, **kwargs)
            if any(s.codigo == servicio.codigo for s in self.__servicios):
                raise ValidacionError("codigo", f"{servicio.codigo} ya existe en el catálogo")
        except SoftwareFJError as error:
            log.warning("Creación de servicio rechazada: %s", error)
            raise
        except TypeError as error:
            # Faltan o sobran argumentos en el constructor -> se encadena
            log.warning("Parámetros incorrectos para %s: %s", clase_servicio.__name__, error)
            raise ValidacionError("servicio", "parámetros de creación incorrectos") from error
        else:
            self.__servicios.append(servicio)
            log.info("Servicio agregado: %s", servicio.describir())
            return servicio

    def buscar_servicio(self, codigo):
        for servicio in self.__servicios:
            if servicio.codigo == str(codigo).upper():
                return servicio
        raise ServicioNoEncontradoError(codigo)

    # ============================ RESERVAS ================================
    def crear_reserva(self, documento_cliente, codigo_servicio, horas, **parametros):
        """Busca cliente y servicio, y crea la reserva (estado PENDIENTE)."""
        try:
            cliente = self.buscar_cliente(documento_cliente)
            servicio = self.buscar_servicio(codigo_servicio)
            reserva = Reserva(cliente, servicio, horas, **parametros)
        except SoftwareFJError as error:
            log.warning("Reserva rechazada (cliente %s, servicio %s): %s",
                        documento_cliente, codigo_servicio, error)
            # Se envuelve en ReservaInvalidaError conservando la causa original
            raise ReservaInvalidaError(f"No se pudo crear la reserva: {error}") from error
        else:
            self.__reservas.append(reserva)
            log.info("Reserva creada: %s", reserva.describir())
            return reserva

    def confirmar_y_procesar(self, reserva, impuesto=None, descuento=0.0):
        """Flujo completo: confirmar y luego procesar el pago."""
        reserva.confirmar()
        return reserva.procesar(impuesto, descuento)

    # ============================ REPORTES ================================
    def resumen(self):
        """Devuelve un texto con el estado actual del sistema."""
        procesadas = [r for r in self.__reservas if r.estado == EstadoReserva.PROCESADA]
        ingresos = sum(r.costo for r in procesadas)
        lineas = [
            f"Clientes registrados : {len(self.__clientes)}",
            f"Servicios en catálogo: {len(self.__servicios)}",
            f"Reservas creadas     : {len(self.__reservas)}",
            f"Reservas procesadas  : {len(procesadas)}",
            f"Ingresos totales     : ${ingresos:,.2f}",
        ]
        return "\n".join(lineas)