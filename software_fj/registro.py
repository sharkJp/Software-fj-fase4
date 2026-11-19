"""
registro.py
Configuración del archivo de logs del sistema.

Se usa el módulo estándar 'logging'. Todos los eventos (INFO) y errores
(WARNING / ERROR) se escriben en logs/software_fj.log. Si el archivo no
se puede crear, los errores se envían a la consola como respaldo.
"""

import logging            # Módulo estándar de Python para registrar eventos
from pathlib import Path  # Manejo de rutas independiente del sistema operativo

# Carpeta donde se guardará el archivo de logs (en la raíz del proyecto)
CARPETA_LOGS = Path(__file__).resolve().parent.parent / "logs"
# Ruta completa del archivo de logs
ARCHIVO_LOG = CARPETA_LOGS / "software_fj.log"


def obtener_logger(nombre="software_fj"):
    """Devuelve un logger configurado. Si ya existe, lo reutiliza
    (así no se duplican los mensajes al importarlo varias veces)."""
    logger = logging.getLogger(nombre)          # Obtiene (o crea) el logger
    if logger.handlers:                         # Si ya tiene manejadores...
        return logger                           # ...ya está configurado

    logger.setLevel(logging.DEBUG)              # Nivel mínimo que se procesa

    try:
        # Creamos la carpeta de logs si no existe
        CARPETA_LOGS.mkdir(parents=True, exist_ok=True)
        # Manejador que escribe en el archivo, en UTF-8 para tildes y eñes
        manejador_archivo = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")
    except OSError as error:
        # Si no se puede escribir el archivo (permisos, disco lleno, etc.)
        # el programa NO se detiene: se usa la consola como respaldo.
        manejador_archivo = None
        print(f"[ADVERTENCIA] No se pudo crear el archivo de logs: {error}")

    # Formato de cada línea: fecha | nivel | módulo | mensaje
    formato = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if manejador_archivo is not None:
        manejador_archivo.setLevel(logging.DEBUG)   # En el archivo va todo
        manejador_archivo.setFormatter(formato)     # Aplicamos el formato
        logger.addHandler(manejador_archivo)        # Lo conectamos al logger
    else:
        # Respaldo: si no hay archivo, al menos los errores salen por consola
        manejador_consola = logging.StreamHandler()
        manejador_consola.setLevel(logging.WARNING)
        manejador_consola.setFormatter(formato)
        logger.addHandler(manejador_consola)

    logger.propagate = False                        # Evita mensajes duplicados

    return logger