import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from Persistencia.databaseSingleton import DatabaseSingleton
from Persistencia.actividadRepository import ActividadRepo
from Persistencia.horarioRepository import HorarioRepo
from Persistencia.inscripcionRepository import InscripcionRepo
from Servicio.inscripcionServicio import InscripcionService
from Modelo.participante import Participante


class TestInscripcionActividadDB(unittest.TestCase):
    def setUp(self):
        # DB en memoria para tests aislados
        self.db = DatabaseSingleton(":memory:")

        # Repositorios y servicio
        self.actividad_repo = ActividadRepo(self.db)
        self.horario_repo = HorarioRepo(self.db)
        self.inscripcion_repo = InscripcionRepo(self.db)
        self.servicio = InscripcionService(db=self.db)

        # Crear actividades y horarios necesarios
        self.aid_tirolesa = self.actividad_repo.crear(
            "Tirolesa", True,
            descripcion="Actividad de altura.",
            terms="Aceptar términos de seguridad."
        )
        self.horario_repo.crear(self.aid_tirolesa, "10:00", 5)

        self.aid_safari = self.actividad_repo.crear(
            "Safari", False,
            descripcion="Recorrido.",
            terms="Aceptar políticas."
        )
        self.horario_repo.crear(self.aid_safari, "15:00", 0)

        self.aid_jard = self.actividad_repo.crear(
            "Jardineria", False,
            descripcion="Actividad de jardinería.",
            terms="Aceptar términos ambientales."
        )
        self.horario_repo.crear(self.aid_jard, "11:00", 3)

    def tearDown(self):
        self.db.close_connection()

    # 1) Inscribirse a actividad con cupo, horario válido, datos y términos aceptados (pasa)
    def test_inscripcion_exitosa_actividad_con_cupo_y_terminos(self):
        print("\nTest 1: Inscripción exitosa con cupo y términos aceptados.")
        participante = Participante(nombre="Juan", dni="12345678", edad=25, talle="M")

        resultado = self.servicio.inscribir(
            nombre_actividad="Tirolesa",
            horario="10:00",
            participantes=[participante],
            aceptar_terminos=True
        )

        print("   Resultado:", resultado)
        self.assertTrue(resultado["exito"])
        self.assertEqual(resultado["mensaje"], "Inscripción realizada con éxito.")
        print("Test 1 completado con éxito.\n")

    # 2) Intentar inscribirse a actividad/hora sin cupo (falla)
    def test_inscripcion_falla_por_no_haber_cupo(self):
        print("\nTest 2: Fallo esperado por falta de cupo.")
        participante = Participante(nombre="María", dni="33333333", edad=30, talle=None)

        resultado = self.servicio.inscribir(
            nombre_actividad="Safari",
            horario="15:00",
            participantes=[participante],
            aceptar_terminos=True
        )

        print("   Resultado:", resultado)
        self.assertFalse(resultado["exito"])
        self.assertIn("cupos", resultado["mensaje"].lower())
        print("Test 2 falló correctamente por falta de cupos.\n")

    # 3) Inscribirse sin talle cuando la actividad NO lo requiere (pasa)
    def test_inscripcion_exitosa_sin_talle_si_no_se_requiere(self):
        print("\nTest 3: Inscripción sin talle en actividad que no lo requiere.")
        participante = Participante(nombre="Laura", dni="22222222", edad=28, talle=None)

        resultado = self.servicio.inscribir(
            nombre_actividad="Jardineria",
            horario="11:00",
            participantes=[participante],
            aceptar_terminos=True
        )

        print("   Resultado:", resultado)
        self.assertTrue(resultado["exito"])
        self.assertEqual(resultado["mensaje"], "Inscripción realizada con éxito.")
        print("Test 3 completado correctamente.\n")

    # 4) Inscribirse en un horario no disponible (falla)
    def test_inscripcion_falla_horario_no_disponible(self):
        print("\nTest 4: Fallo esperado por horario no disponible.")
        participante = Participante(nombre="Pedro", dni="44444444", edad=40, talle="L")

        resultado = self.servicio.inscribir(
            nombre_actividad="Tirolesa",
            horario="22:00",  # no creado en setUp
            participantes=[participante],
            aceptar_terminos=True
        )

        print("   Resultado:", resultado)
        self.assertFalse(resultado["exito"])
        self.assertIn("horario", resultado["mensaje"].lower())
        print("Test 4 falló correctamente por horario inexistente.\n")

    # 5) Intentar inscribirse sin aceptar los términos y condiciones (falla)
    def test_inscripcion_falla_por_no_aceptar_terminos(self):
        print("\nTest 5: Fallo esperado por no aceptar los términos.")
        participante = Participante(nombre="Sofía", dni="55555555", edad=22, talle="M")

        resultado = self.servicio.inscribir(
            nombre_actividad="Tirolesa",
            horario="10:00",
            participantes=[participante],
            aceptar_terminos=False
        )

        print("   Resultado:", resultado)
        self.assertFalse(resultado["exito"])
        self.assertIn("términos", resultado["mensaje"].lower())
        print("Test 5 falló correctamente por no aceptar términos.\n")

    # 6) Intentar inscribirse sin talle cuando la actividad SÍ lo requiere (falla)
    def test_inscripcion_falla_por_falta_de_talle_en_actividad_que_lo_requiere(self):
        print("\nTest 6: Fallo esperado por falta de talle en actividad que lo requiere.")
        participante = Participante(nombre="Ana", dni="66666666", edad=27, talle=None)

        resultado = self.servicio.inscribir(
            nombre_actividad="Tirolesa",
            horario="10:00",
            participantes=[participante],
            aceptar_terminos=True
        )

        print("   Resultado:", resultado)
        self.assertFalse(resultado["exito"])
        self.assertIn("talle", resultado["mensaje"].lower())
        print("Test 6 falló correctamente por falta de talle.\n")


if __name__ == '__main__':
    unittest.main(verbosity=2)
