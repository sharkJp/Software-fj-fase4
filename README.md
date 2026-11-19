# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

**Curso:** Programación (213023) – UNAD
**Actividad:** Fase 4 – Componente práctico – Prácticas simuladas
**Autor:** Jhon Gerardo Plazas Vargas

> 🚧 Proyecto en desarrollo.

## Descripción

Sistema orientado a objetos en Python, **sin base de datos**, que gestiona clientes,
servicios (reserva de salas, alquiler de equipos y asesorías) y reservas para la
empresa Software FJ. Aplica abstracción, herencia, polimorfismo, encapsulación y
manejo avanzado de excepciones. Los eventos y errores se registran en un archivo de logs.

## Roles de trabajo

| Rol | Rama | Archivos |
|---|---|---|
| 1. Excepciones y logs | `feature/excepciones-logs` | `excepciones.py`, `registro.py` |
| 2. Entidad y Cliente | `feature/entidad-cliente` | `entidad.py`, `cliente.py` |
| 3. Servicios | `feature/servicios` | `servicios.py` |
| 4. Reservas | `feature/reservas` | `reserva.py` |
| 5. Sistema, simulaciones y pruebas | `feature/sistema-simulaciones` | `sistema.py`, `main.py`, `tests/` |

## Requisitos

- Python 3.10 o superior (no usa librerías externas)