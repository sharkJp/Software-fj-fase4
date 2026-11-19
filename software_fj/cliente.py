"""
cliente.py
Clase Cliente con encapsulación de datos personales y validaciones robustas.
"""

import re                                   # Expresiones regulares para validar formatos
from .entidad import Entidad                # Clase base abstracta
from .excepciones import ValidacionError, ParametroFaltanteError

# Patrones de validación (compilados una sola vez para eficiencia)
PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]{3,60}$")   # Letras y espacios
PATRON_DOCUMENTO = re.compile(r"^\d{6,12}$")                       # 6 a 12 dígitos
PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")          # usuario@dominio.ext
PATRON_TELEFONO = re.compile(r"^3\d{9}$")                          # Celular colombiano


class Cliente(Entidad):
    """Representa a un cliente de Software FJ."""

    def __init__(self, nombre, documento, correo, telefono=None):
        super().__init__()                  # Asigna ID y fecha de creación
        # Se usan los setters: cada asignación pasa por su validación
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.telefono = telefono

    # ----------------------------- nombre ---------------------------------
    @property
    def nombre(self):
        return self.__nombre                # Atributo privado (encapsulado)

    @nombre.setter
    def nombre(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("nombre")          # Falta el dato
        valor = " ".join(str(valor).split())                # Quita espacios extra
        if not PATRON_NOMBRE.match(valor):
            raise ValidacionError("nombre", "solo letras y espacios (3 a 60 caracteres)")
        self.__nombre = valor.title()                       # Guarda con mayúscula inicial

    # ---------------------------- documento -------------------------------
    @property
    def documento(self):
        return self.__documento

    @documento.setter
    def documento(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("documento")
        valor = str(valor).strip()
        if not PATRON_DOCUMENTO.match(valor):
            raise ValidacionError("documento", "debe tener entre 6 y 12 dígitos numéricos")
        self.__documento = valor

    # ----------------------------- correo ---------------------------------
    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("correo")
        valor = str(valor).strip().lower()                  # Correo en minúsculas
        if not PATRON_CORREO.match(valor):
            raise ValidacionError("correo", f"'{valor}' no tiene un formato válido")
        self.__correo = valor

    # ---------------------------- teléfono --------------------------------
    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        if valor is None:                   # El teléfono es opcional
            self.__telefono = None
            return
        valor = str(valor).replace(" ", "")
        if not PATRON_TELEFONO.match(valor):
            raise ValidacionError("telefono", "debe ser un celular de 10 dígitos que inicie en 3")
        self.__telefono = valor

    # ------------------------ métodos abstractos ---------------------------
    def validar(self):
        """Revalida todos los campos reasignándolos (útil tras cambios)."""
        self.nombre = self.nombre
        self.documento = self.documento
        self.correo = self.correo
        self.telefono = self.telefono
        return True

    def describir(self):
        # Se enmascara el documento para proteger el dato personal
        doc_oculto = "*" * (len(self.documento) - 4) + self.documento[-4:]
        return f"Cliente #{self.id}: {self.nombre} (doc. {doc_oculto}, {self.correo})"