import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import unicodedata
from Persistencia.database_singleton import DatabaseSingleton
from Persistencia.actividad_repository import ActividadRepo
from Persistencia.horario_repository import HorarioRepo
from Persistencia.inscripcion_repository import InscripcionRepo
from Persistencia.participante_repository import ParticipanteRepo
from Servicio.inscripcion_servicio import InscripcionService
from Modelo.participante import Participante



def norm(s: str) -> str:
    """Normaliza texto (quita tildes y pone en minúsculas) para comparar mensajes."""
    if s is None:
        return ""
    return unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII").lower()

class TestInscripcionActividadDB(unittest.TestCase):
    def setUp(self):
        # DB en memoria para tests aislados
        self.db = DatabaseSingleton(":memory:")

        # Repositorios y servicio
        self.actividad_repo = ActividadRepo(self.db)
        self.horario_repo = HorarioRepo(self.db)
        self.participante_repo = ParticipanteRepo(self.db)
        self.inscripcion_repo = InscripcionRepo(self.db)
        self.servicio = InscripcionService(db=self.db)

        # Crear actividades y horarios necesarios
        self.aid_tirolesa = self.actividad_repo.crear(
            "Tirolesa", True,
            descripcion="Actividad de altura.",
            terms="Edad mínima 12 años. Aceptar términos de seguridad."
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
        test_id = "TEST 1"
        desc = "Inscripción exitosa: actividad con cupo y términos aceptados"
        participante = Participante(nombre="Juan", dni="12345678", edad=25, talle="M")

        try:
            resultado = self.servicio.inscribir(
                nombre_actividad="Tirolesa",
                horario="10:00",
                participantes=[participante],
                aceptar_terminos=True
            )

            # Resultado esperado
            self.assertTrue(resultado["exito"])
            self.assertEqual(norm(resultado["mensaje"]), norm("Inscripción realizada con éxito."))

            # Verificar cupo decrementado en la BD
            h = self.horario_repo.obtener_por_actividad_y_hora(self.aid_tirolesa, "10:00")
            self.assertIsNotNone(h)
            self.assertEqual(h["cupos"], 4)

            # Verificar que se registró la inscripción
            inscripciones = self.inscripcion_repo.listar_por_horario(h["id"])
            self.assertEqual(len(inscripciones), 1)
            self.assertEqual(inscripciones[0]["dni"], "12345678")

        except AssertionError as e:
            print(f"[{test_id}] FAIL - {desc} -> {e}")
            raise
        except Exception as e:
            print(f"[{test_id}] ERROR inesperado - {desc} -> {e}")
            raise
        else:
            print(f"[{test_id}] PASS - {desc}")

    # 2) Intentar inscribirse a actividad/hora sin cupo (falla)
    def test_inscripcion_falla_por_no_haber_cupo(self):
        test_id = "TEST 2"
        desc = "Fallo esperado: no hay cupos en el horario"
        participante = Participante(nombre="María", dni="33333333", edad=30, talle=None)

        try:
            resultado = self.servicio.inscribir(
                nombre_actividad="Safari",
                horario="15:00",
                participantes=[participante],
                aceptar_terminos=True
            )

            # Debe fallar por cupos
            self.assertFalse(resultado["exito"])
            self.assertIn("cupos", norm(resultado["mensaje"]))

            # Verificar que el cupo no cambió y no se registraron inscripciones
            h = self.horario_repo.obtener_por_actividad_y_hora(self.aid_safari, "15:00")
            self.assertIsNotNone(h)
            self.assertEqual(h["cupos"], 0)
            inscripciones = self.inscripcion_repo.listar_por_horario(h["id"])
            self.assertEqual(len(inscripciones), 0)

        except AssertionError as e:
            print(f"[{test_id}] FAIL - {desc} -> {e}")
            raise
        except Exception as e:
            print(f"[{test_id}] ERROR inesperado - {desc} -> {e}")
            raise
        else:
            print(f"[{test_id}] PASS - {desc}")

    # 3) Inscribirse sin talle cuando la actividad NO lo requiere (pasa)
    def test_inscripcion_exitosa_sin_talle_si_no_se_requiere(self):
        test_id = "TEST 3"
        desc = "Inscripción exitosa: actividad que no requiere talle"
        participante = Participante(nombre="Laura", dni="22222222", edad=28, talle=None)

        try:
            resultado = self.servicio.inscribir(
                nombre_actividad="Jardineria",
                horario="11:00",
                participantes=[participante],
                aceptar_terminos=True
            )

            self.assertTrue(resultado["exito"])
            self.assertEqual(norm(resultado["mensaje"]), norm("Inscripción realizada con éxito."))

            # Verificar decremento y registro
            h = self.horario_repo.obtener_por_actividad_y_hora(self.aid_jard, "11:00")
            self.assertIsNotNone(h)
            self.assertEqual(h["cupos"], 2)
            inscripciones = self.inscripcion_repo.listar_por_horario(h["id"])
            self.assertEqual(len(inscripciones), 1)
            self.assertEqual(inscripciones[0]["dni"], "22222222")

        except AssertionError as e:
            print(f"[{test_id}] FAIL - {desc} -> {e}")
            raise
        except Exception as e:
            print(f"[{test_id}] ERROR inesperado - {desc} -> {e}")
            raise
        else:
            print(f"[{test_id}] PASS - {desc}")

    # 4) Inscribirse en un horario no disponible (falla)
    def test_inscripcion_falla_horario_no_disponible(self):
        test_id = "TEST 4"
        desc = "Fallo esperado: horario no disponible para la actividad"
        participante = Participante(nombre="Pedro", dni="44444444", edad=40, talle="L")

        try:
            resultado = self.servicio.inscribir(
                nombre_actividad="Tirolesa",
                horario="22:00",  # no creado en setUp
                participantes=[participante],
                aceptar_terminos=True
            )

            self.assertFalse(resultado["exito"])
            self.assertIn("horario", norm(resultado["mensaje"]))

            # Verificar que no se creó ninguna inscripción para la actividad
            horarios = self.horario_repo.listar_por_actividad(self.aid_tirolesa)
            total_ins = 0
            for hr in horarios:
                total_ins += len(self.inscripcion_repo.listar_por_horario(hr["id"]))
            self.assertEqual(total_ins, 0)

        except AssertionError as e:
            print(f"[{test_id}] FAIL - {desc} -> {e}")
            raise
        except Exception as e:
            print(f"[{test_id}] ERROR inesperado - {desc} -> {e}")
            raise
        else:
            print(f"[{test_id}] PASS - {desc}")

    # 5) Intentar inscribirse sin aceptar los términos y condiciones (falla)
    def test_inscripcion_falla_por_no_aceptar_terminos(self):
        test_id = "TEST 5"
        desc = "Fallo esperado: no aceptar términos y condiciones"
        participante = Participante(nombre="Sofía", dni="55555555", edad=22, talle="M")

        try:
            resultado = self.servicio.inscribir(
                nombre_actividad="Tirolesa",
                horario="10:00",
                participantes=[participante],
                aceptar_terminos=False
            )

            self.assertFalse(resultado["exito"])
            self.assertIn("termin", norm(resultado["mensaje"]))  # busca "termin" para cubrir "términos"/"terminos"

            # Verificar que no se registró la inscripción y que cupo no cambió
            h = self.horario_repo.obtener_por_actividad_y_hora(self.aid_tirolesa, "10:00")
            self.assertIsNotNone(h)
            self.assertEqual(h["cupos"], 5)
            inscripciones = self.inscripcion_repo.listar_por_horario(h["id"])
            self.assertEqual(len(inscripciones), 0)

        except AssertionError as e:
            print(f"[{test_id}] FAIL - {desc} -> {e}")
            raise
        except Exception as e:
            print(f"[{test_id}] ERROR inesperado - {desc} -> {e}")
            raise
        else:
            print(f"[{test_id}] PASS - {desc}")

    # 6) Intentar inscribirse sin talle cuando la actividad SÍ lo requiere (falla)
    def test_inscripcion_falla_por_falta_de_talle_en_actividad_que_lo_requiere(self):
        test_id = "TEST 6"
        desc = "Fallo esperado: falta de talle en actividad que lo requiere"
        participante = Participante(nombre="Ana", dni="66666666", edad=27, talle=None)

        try:
            resultado = self.servicio.inscribir(
                nombre_actividad="Tirolesa",
                horario="10:00",
                participantes=[participante],
                aceptar_terminos=True
            )

            self.assertFalse(resultado["exito"])
            self.assertIn("talle", norm(resultado["mensaje"]))

            # Verificar que no se registró la inscripción y que cupo no cambió
            h = self.horario_repo.obtener_por_actividad_y_hora(self.aid_tirolesa, "10:00")
            self.assertIsNotNone(h)
            self.assertEqual(h["cupos"], 5)
            inscripciones = self.inscripcion_repo.listar_por_horario(h["id"])
            self.assertEqual(len(inscripciones), 0)

        except AssertionError as e:
            print(f"[{test_id}] FAIL - {desc} -> {e}")
            raise
        except Exception as e:
            print(f"[{test_id}] ERROR inesperado - {desc} -> {e}")
            raise
        else:
            print(f"[{test_id}] PASS - {desc}")


if __name__ == '__main__':
    unittest.main(verbosity=2)