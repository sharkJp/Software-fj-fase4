"""
main.py
Simulación de operaciones del Sistema Integral de Gestión de Clientes,
Servicios y Reservas de Software FJ.

Ejecuta operaciones válidas e inválidas para demostrar que la aplicación
NUNCA se detiene: cada error se captura, se registra en logs/software_fj.log
y el programa continúa con la siguiente operación.

Ejecutar con:  python main.py
"""

from software_fj import (
    SistemaGestion, ReservaSala, AlquilerEquipo, Asesoria,
)
from software_fj.excepciones import SoftwareFJError
from software_fj.registro import obtener_logger, ARCHIVO_LOG

log = obtener_logger("software_fj.main")

# Contadores de resultados de la simulación
resultados = {"exitosas": 0, "controladas": 0, "inesperadas": 0}


def ejecutar(numero, descripcion, operacion):
    """
    Ejecuta una operación de forma segura.
    try / except / else / finally: pase lo que pase, el programa sigue.
    """
    print(f"\n[{numero:02d}] {descripcion}")
    log.info("SIMULACIÓN %02d: %s", numero, descripcion)
    try:
        resultado = operacion()                       # Se intenta la operación
    except SoftwareFJError as error:
        # Error previsto del dominio: se informa y se registra
        resultados["controladas"] += 1
        print(f"   ✗ Error controlado: {error}")
        causa = error.__cause__                       # ¿Viene encadenado?
        while causa is not None:                      # Recorre toda la cadena
            print(f"     ↳ Causado por {type(causa).__name__}: {causa}")
            causa = causa.__cause__
        log.error("Simulación %02d falló de forma controlada: %s", numero, error)
    except Exception as error:                        # Red de seguridad
        # Error NO previsto: se registra con traza completa, pero no se detiene
        resultados["inesperadas"] += 1
        print(f"   ✗ Error inesperado: {type(error).__name__}: {error}")
        log.exception("Simulación %02d: error inesperado", numero)
    else:
        # Solo si la operación fue exitosa
        resultados["exitosas"] += 1
        if isinstance(resultado, float):              # Los costos se muestran como dinero
            resultado = f"Total a pagar ${resultado:,.2f}"
        print(f"   ✓ OK: {resultado}")
    finally:
        # Siempre se ejecuta: marca el fin de la operación en el log
        log.debug("Simulación %02d terminada", numero)


def main():
    sistema = SistemaGestion()
    print("=" * 70)
    print("  SOFTWARE FJ - Simulación del sistema de clientes, servicios y reservas")
    print("=" * 70)

    # ---------------------------- CLIENTES --------------------------------
    ejecutar(1, "Registrar cliente válido (Ana)",
             lambda: sistema.registrar_cliente("ana maría torres", "1117500123",
                                               "ana.torres@correo.com", "3101234567"))
    ejecutar(2, "Registrar cliente válido (Carlos)",
             lambda: sistema.registrar_cliente("Carlos Pérez", "40765432",
                                               "carlos@empresa.co"))
    ejecutar(3, "Registrar cliente con correo inválido",
             lambda: sistema.registrar_cliente("Luis Gómez", "1006789012", "luis-arroba-mail"))
    ejecutar(4, "Registrar cliente con documento duplicado",
             lambda: sistema.registrar_cliente("Ana Copia", "1117500123", "copia@correo.com"))
    ejecutar(5, "Registrar cliente sin nombre (parámetro faltante)",
             lambda: sistema.registrar_cliente("", "998877665", "x@correo.com"))

    # ---------------------------- SERVICIOS -------------------------------
    ejecutar(6, "Crear servicio: Sala de juntas",
             lambda: sistema.agregar_servicio(ReservaSala, "SAL-01", "Sala Amazonía",
                                              50000, capacidad=15))
    ejecutar(7, "Crear servicio: Alquiler de portátiles",
             lambda: sistema.agregar_servicio(AlquilerEquipo, "EQP-01", "Portátil Dell",
                                              8000, unidades_disponibles=5))
    ejecutar(8, "Crear servicio: Asesoría en ciberseguridad",
             lambda: sistema.agregar_servicio(Asesoria, "ASE-01", "Auditoría de seguridad",
                                              120000, especialidad="Ciberseguridad"))
    ejecutar(9, "Crear servicio con tarifa negativa",
             lambda: sistema.agregar_servicio(ReservaSala, "SAL-02", "Sala Caquetá",
                                              -1000, capacidad=10))
    ejecutar(10, "Crear servicio con parámetros faltantes (encadenamiento)",
             lambda: sistema.agregar_servicio(AlquilerEquipo, "EQP-02", "Proyector", 5000))

    # ---------------------------- RESERVAS --------------------------------
    ejecutar(11, "Reserva válida de sala: confirmar y procesar (IVA por defecto)",
             lambda: sistema.confirmar_y_procesar(
                 sistema.crear_reserva("1117500123", "SAL-01", 3, personas=10)))
    ejecutar(12, "Reserva de sala que supera la capacidad",
             lambda: sistema.crear_reserva("40765432", "SAL-01", 2, personas=40))
    ejecutar(13, "Reserva con duración no numérica ('tres')",
             lambda: sistema.crear_reserva("40765432", "ASE-01", "tres", nivel="experto"))
    ejecutar(14, "Reserva de un cliente que no existe",
             lambda: sistema.crear_reserva("123456789", "SAL-01", 2, personas=5))
    ejecutar(15, "Reserva de asesoría experta con 10 % de descuento",
             lambda: sistema.confirmar_y_procesar(
                 sistema.crear_reserva("40765432", "ASE-01", 2, nivel="experto"),
                 descuento=0.10))

    def servicio_no_disponible():
        sistema.buscar_servicio("EQP-01").desactivar()       # Equipos en mantenimiento
        try:
            return sistema.crear_reserva("1117500123", "EQP-01", 4, cantidad=2)
        finally:
            sistema.buscar_servicio("EQP-01").activar()      # try/finally: se reactiva siempre
    ejecutar(16, "Reserva de servicio NO disponible (en mantenimiento)", servicio_no_disponible)

    ejecutar(17, "Alquiler de 3 portátiles sin impuesto (sobrecarga: impuesto=0)",
             lambda: sistema.confirmar_y_procesar(
                 sistema.crear_reserva("1117500123", "EQP-01", 5, cantidad=3), impuesto=0))

    def cancelar_y_procesar():
        reserva = sistema.crear_reserva("40765432", "SAL-01", 1, personas=4)
        reserva.cancelar("El cliente cambió de fecha")
        return reserva.procesar()                           # Operación no permitida
    ejecutar(18, "Cancelar una reserva y luego intentar procesarla", cancelar_y_procesar)

    ejecutar(19, "Procesar reserva con descuento inconsistente (150 %)",
             lambda: sistema.confirmar_y_procesar(
                 sistema.crear_reserva("1117500123", "ASE-01", 1), descuento=1.5))

    def demostrar_sobrecarga():
        asesoria = sistema.buscar_servicio("ASE-01")
        v1 = asesoria.calcular_costo(2)                       # Solo horas
        v2 = asesoria.calcular_costo(2, 0.05)                 # Horas + impuesto
        v3 = asesoria.calcular_costo(2, 0.19, 0.20, nivel="avanzado")  # Todo
        return f"(2h) ${v1:,.0f} | (2h, 5%) ${v2:,.0f} | (2h, IVA, -20%, avanzado) ${v3:,.0f}"
    ejecutar(20, "Demostración de sobrecarga de calcular_costo", demostrar_sobrecarga)

    # ---------------------------- RESUMEN ---------------------------------
    print("\n" + "=" * 70)
    print("  RESUMEN FINAL")
    print("=" * 70)
    print(sistema.resumen())
    print("\nReservas registradas:")
    for reserva in sistema.reservas:
        print("  -", reserva)
    print(f"\nOperaciones exitosas: {resultados['exitosas']} | "
          f"Errores controlados: {resultados['controladas']} | "
          f"Errores inesperados: {resultados['inesperadas']}")
    print(f"Log completo en: {ARCHIVO_LOG}")
    log.info("Simulación terminada: %s", resultados)


if __name__ == "__main__":
    main()