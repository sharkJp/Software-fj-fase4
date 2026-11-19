"""
Pruebas unitarias del sistema Software FJ.
Ejecutar desde la raíz del proyecto con:  python -m unittest -v
"""

import unittest
from software_fj import SistemaGestion, ReservaSala, AlquilerEquipo, Asesoria, EstadoReserva
from software_fj.excepciones import (
    ValidacionError, ParametroFaltanteError, ClienteDuplicadoError,
    ReservaInvalidaError, OperacionNoPermitidaError, CalculoError,
)
from software_fj.entidad import Entidad
from software_fj.servicios import Servicio


class TestSistema(unittest.TestCase):

    def setUp(self):
        # Antes de cada prueba se crea un sistema limpio con datos base
        self.s = SistemaGestion()
        self.s.registrar_cliente("Ana Torres", "1117500123", "ana@correo.com")
        self.s.agregar_servicio(ReservaSala, "SAL-01", "Sala A", 50000, capacidad=10)
        self.s.agregar_servicio(AlquilerEquipo, "EQP-01", "Portátil", 8000, unidades_disponibles=2)
        self.s.agregar_servicio(Asesoria, "ASE-01", "Asesoría", 100000, especialidad="Redes")

    def test_clases_abstractas_no_se_instancian(self):
        with self.assertRaises(TypeError):
            Entidad()
        with self.assertRaises(TypeError):
            Servicio("X", "Y", 1000)

    def test_cliente_invalido(self):
        with self.assertRaises(ValidacionError):
            self.s.registrar_cliente("Luis", "abc", "luis@correo.com")
        with self.assertRaises(ParametroFaltanteError):
            self.s.registrar_cliente(None, "12345678", "x@correo.com")

    def test_cliente_duplicado(self):
        with self.assertRaises(ClienteDuplicadoError):
            self.s.registrar_cliente("Otra Ana", "1117500123", "otra@correo.com")

    def test_polimorfismo_costos(self):
        # Mismo método, resultado distinto según el tipo de servicio
        sala = self.s.buscar_servicio("SAL-01").calcular_costo(2, 0, personas=5)
        equipo = self.s.buscar_servicio("EQP-01").calcular_costo(2, 0, cantidad=1)
        asesoria = self.s.buscar_servicio("ASE-01").calcular_costo(2, 0, nivel="experto")
        self.assertEqual(sala, 100000)
        self.assertEqual(equipo, 36000)        # 8000*2 + 20000 de depósito
        self.assertEqual(asesoria, 400000)     # 100000*2*2.0

    def test_sobrecarga_calcular_costo(self):
        ase = self.s.buscar_servicio("ASE-01")
        self.assertEqual(ase.calcular_costo(1), 119000)          # IVA por defecto
        self.assertEqual(ase.calcular_costo(1, 0), 100000)       # Sin impuesto
        self.assertEqual(ase.calcular_costo(1, 0, 0.5), 50000)   # Con descuento

    def test_flujo_reserva_exitosa(self):
        r = self.s.crear_reserva("1117500123", "SAL-01", 2, personas=4)
        self.s.confirmar_y_procesar(r, impuesto=0)
        self.assertEqual(r.estado, EstadoReserva.PROCESADA)
        self.assertEqual(r.costo, 100000)

    def test_encadenamiento_de_excepciones(self):
        with self.assertRaises(ReservaInvalidaError) as ctx:
            self.s.crear_reserva("1117500123", "ASE-01", "dos")
        # La excepción conserva su causa original
        self.assertIsNotNone(ctx.exception.__cause__)

    def test_operacion_no_permitida(self):
        r = self.s.crear_reserva("1117500123", "SAL-01", 1, personas=2)
        r.cancelar()
        with self.assertRaises(OperacionNoPermitidaError):
            r.confirmar()

    def test_calculo_inconsistente(self):
        r = self.s.crear_reserva("1117500123", "ASE-01", 1)
        r.confirmar()
        with self.assertRaises(CalculoError):
            r.procesar(descuento=2)


if __name__ == "__main__":
    unittest.main()