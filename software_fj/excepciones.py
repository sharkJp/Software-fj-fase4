"""
excepciones.py
Excepciones personalizadas del sistema Software FJ.

Todas heredan de SoftwareFJError, de modo que el programa principal
puede capturar cualquier error propio del dominio con un solo except,
sin confundirlo con errores internos de Python.
"""


class SoftwareFJError(Exception):
    """Excepción base de todo el sistema Software FJ."""

    def __init__(self, mensaje, codigo="FJ-000"):
        # Llamamos al constructor de Exception para conservar el mensaje
        super().__init__(mensaje)
        # Guardamos un código corto que facilita buscar el error en el log
        self.codigo = codigo

    def __str__(self):
        # Representación legible: [código] mensaje
        return f"[{self.codigo}] {self.args[0]}"


# ---------------------------------------------------------------------------
# Errores de validación de datos
# ---------------------------------------------------------------------------
class ValidacionError(SoftwareFJError):
    """Se lanza cuando un dato no cumple las reglas de validación."""

    def __init__(self, campo, mensaje):
        # Indicamos qué campo falló para que el mensaje sea preciso
        super().__init__(f"Campo '{campo}': {mensaje}", codigo="FJ-100")
        # Guardamos el nombre del campo por si se necesita después
        self.campo = campo


class ParametroFaltanteError(ValidacionError):
    """Se lanza cuando falta un parámetro obligatorio."""

    def __init__(self, campo):
        # Reutilizamos ValidacionError con un mensaje estándar
        super().__init__(campo, "es obligatorio y no fue suministrado")
        # Código específico para parámetros faltantes
        self.codigo = "FJ-101"


# ---------------------------------------------------------------------------
# Errores de clientes
# ---------------------------------------------------------------------------
class ClienteError(SoftwareFJError):
    """Errores relacionados con la gestión de clientes."""

    def __init__(self, mensaje):
        super().__init__(mensaje, codigo="FJ-200")


class ClienteDuplicadoError(ClienteError):
    """Se lanza al intentar registrar un cliente con un documento ya existente."""

    def __init__(self, documento):
        super().__init__(f"Ya existe un cliente con documento {documento}")
        self.codigo = "FJ-201"


class ClienteNoEncontradoError(ClienteError):
    """Se lanza cuando se busca un cliente que no está registrado."""

    def __init__(self, documento):
        super().__init__(f"No existe un cliente con documento {documento}")
        self.codigo = "FJ-202"


# ---------------------------------------------------------------------------
# Errores de servicios
# ---------------------------------------------------------------------------
class ServicioError(SoftwareFJError):
    """Errores relacionados con los servicios ofrecidos."""

    def __init__(self, mensaje):
        super().__init__(mensaje, codigo="FJ-300")


class ServicioNoDisponibleError(ServicioError):
    """Se lanza cuando un servicio existe pero no está disponible."""

    def __init__(self, nombre_servicio):
        super().__init__(f"El servicio '{nombre_servicio}' no está disponible")
        self.codigo = "FJ-301"


class ServicioNoEncontradoError(ServicioError):
    """Se lanza cuando se busca un servicio que no existe en el catálogo."""

    def __init__(self, codigo_servicio):
        super().__init__(f"No existe un servicio con código {codigo_servicio}")
        self.codigo = "FJ-302"


# ---------------------------------------------------------------------------
# Errores de reservas
# ---------------------------------------------------------------------------
class ReservaError(SoftwareFJError):
    """Errores relacionados con las reservas."""

    def __init__(self, mensaje):
        super().__init__(mensaje, codigo="FJ-400")


class ReservaInvalidaError(ReservaError):
    """Se lanza cuando los datos de una reserva no son coherentes."""

    def __init__(self, mensaje):
        super().__init__(mensaje)
        self.codigo = "FJ-401"


class OperacionNoPermitidaError(ReservaError):
    """Se lanza cuando se intenta una transición de estado prohibida
    (por ejemplo, confirmar una reserva ya cancelada)."""

    def __init__(self, mensaje):
        super().__init__(mensaje)
        self.codigo = "FJ-402"


# ---------------------------------------------------------------------------
# Errores de cálculo
# ---------------------------------------------------------------------------
class CalculoError(SoftwareFJError):
    """Se lanza cuando un cálculo de costos produce un resultado inconsistente."""

    def __init__(self, mensaje):
        super().__init__(mensaje, codigo="FJ-500")