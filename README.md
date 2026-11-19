# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

- **Curso:** Programación (213023) – UNAD
- **Actividad:** Fase 4 – Componente práctico – Prácticas simuladas
- **Autor:** Jhon Gerardo Plazas Vargas

## Descripción

Sistema orientado a objetos en Python, **sin base de datos**, que gestiona clientes,
servicios (reserva de salas, alquiler de equipos y asesorías) y reservas para la
empresa Software FJ. Aplica abstracción, herencia, polimorfismo, encapsulación y
**manejo avanzado de excepciones**: la aplicación nunca se detiene ante un error y
registra todos los eventos en un archivo de logs.

## Cómo ejecutar

Requiere Python 3.10 o superior. No usa librerías externas.

    python main.py              # Ejecuta las 20 simulaciones
    python -m unittest -v       # Ejecuta las 9 pruebas unitarias

El registro de eventos y errores queda en `logs/software_fj.log`.

## Estructura del proyecto

    Software-fj-fase4/
    ├── main.py                  # 20 simulaciones (válidas e inválidas)
    ├── software_fj/
    │   ├── excepciones.py       # Jerarquía de excepciones personalizadas
    │   ├── registro.py          # Configuración del archivo de logs
    │   ├── entidad.py           # Clase abstracta Entidad
    │   ├── cliente.py           # Clase Cliente (encapsulación y validaciones)
    │   ├── servicios.py         # Servicio (abstracta) + ReservaSala, AlquilerEquipo, Asesoria
    │   ├── reserva.py           # Clase Reserva (confirmar, cancelar, procesar)
    │   └── sistema.py           # SistemaGestion: listas internas y operaciones
    ├── tests/test_sistema.py    # Pruebas unitarias
    └── capturas/                # Evidencias de ejecución

## Requisitos del Anexo 3 y dónde se cumplen

| Requisito | Implementación |
|---|---|
| Clase abstracta general | `Entidad` con `validar()` y `describir()` abstractos |
| Cliente con validaciones y encapsulación | Atributos privados, `@property` y validación con expresiones regulares |
| Servicio abstracto + 3 especializados | `Servicio` → `ReservaSala`, `AlquilerEquipo`, `Asesoria` |
| Polimorfismo y métodos sobrescritos | `calcular_costo_base`, `validar_parametros` y `describir` en cada servicio |
| Métodos sobrecargados | `calcular_costo(horas[, impuesto[, descuento]])` con `@overload` |
| Reserva con estados | Pendiente → Confirmada → Procesada / Cancelada |
| Excepciones personalizadas | 12 clases que heredan de `SoftwareFJError` |
| `try/except/else` | `SistemaGestion.registrar_cliente`, `agregar_servicio`, `crear_reserva` |
| `try/except/else/finally` | `Reserva.procesar` y `main.ejecutar` |
| `try/finally` | Simulación 16 (reactiva el servicio pase lo que pase) |
| Encadenamiento (`raise ... from`) | `Reserva.__init__`, `Reserva.procesar`, `SistemaGestion.crear_reserva` |
| Archivo de logs | `logs/software_fj.log` (INFO, WARNING, ERROR, DEBUG) |
| ≥ 10 simulaciones | 20 simulaciones: 9 exitosas, 11 errores controlados, 0 inesperados |

## Jerarquía de excepciones

    SoftwareFJError (FJ-000)
    ├── ValidacionError (FJ-100)
    │   └── ParametroFaltanteError (FJ-101)
    ├── ClienteError (FJ-200)
    │   ├── ClienteDuplicadoError (FJ-201)
    │   └── ClienteNoEncontradoError (FJ-202)
    ├── ServicioError (FJ-300)
    │   ├── ServicioNoDisponibleError (FJ-301)
    │   └── ServicioNoEncontradoError (FJ-302)
    ├── ReservaError (FJ-400)
    │   ├── ReservaInvalidaError (FJ-401)
    │   └── OperacionNoPermitidaError (FJ-402)
    └── CalculoError (FJ-500)

## Roles de trabajo

| Rol | Issue | Rama | Pull Request |
|---|---|---|---|
| 1. Excepciones y logs | #1 | `feature/excepciones-logs` | #6 |
| 2. Entidad y Cliente | #2 | `feature/entidad-cliente` | #7 |
| 3. Servicios | #3 | `feature/servicios` | #8 |
| Corrección de tipos | – | `fix/servicios-tipos` | #9 |
| 4. Reservas | #4 | `feature/reservas` | #10 |
| 5. Sistema, simulaciones y pruebas | #5 | `feature/sistema-simulaciones` | #11 |

Cada módulo se probó de forma independiente antes de integrarse a `main`.

## Evidencias de ejecución

### Simulaciones
![Inicio de la simulación](capturas/simulacion_inicio.png)
![Resumen final](capturas/simulacion_resumen.png)

### Pruebas unitarias
![Pruebas unitarias](capturas/pruebas.png)

### Archivo de logs
![Archivo de logs](capturas/log.png)