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

        # Crear actividades y horarios necesarios para las 4 pruebas:
        # - Tirolesa (requiere talle)
        # - Safari (usada para horario sin cupo)
        # - Jardineria (no requiere talle)
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
        # horario con 0 cupos para probar falla por no cupo
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
        participante = Participante(nombre="Juan", dni="12345678", edad=25, talle="M")

        resultado = self.servicio.inscribir(
            nombre_actividad="Tirolesa",
            horario="10:00",
            participantes=[participante],
            aceptar_terminos=True
        )

        self.assertTrue(resultado["exito"])
        self.assertEqual(resultado["mensaje"], "Inscripción realizada con éxito.")

    # 2) Intentar inscribirse a actividad/hora sin cupo (falla)
    def test_inscripcion_falla_por_no_haber_cupo(self):
        participante = Participante(nombre="María", dni="33333333", edad=30, talle=None)

        resultado = self.servicio.inscribir(
            nombre_actividad="Safari",
            horario="15:00",
            participantes=[participante],
            aceptar_terminos=True
        )

        self.assertFalse(resultado["exito"])
        # Mensaje provisto por el servicio: "No hay cupos suficientes para ese horario."
        self.assertIn("cupos", resultado["mensaje"].lower())

    # 3) Inscribirse sin talle cuando la actividad NO lo requiere (pasa)
    def test_inscripcion_exitosa_sin_talle_si_no_se_requiere(self):
        participante = Participante(nombre="Laura", dni="22222222", edad=28, talle=None)

        resultado = self.servicio.inscribir(
            nombre_actividad="Jardineria",
            horario="11:00",
            participantes=[participante],
            aceptar_terminos=True
        )

        self.assertTrue(resultado["exito"])
        self.assertEqual(resultado["mensaje"], "Inscripción realizada con éxito.")

    # 4) Inscribirse en un horario donde la actividad no está disponible / parque cerrado (falla)
    def test_inscripcion_falla_horario_no_disponible(self):
        participante = Participante(nombre="Pedro", dni="44444444", edad=40, talle="L")

        # Intentamos un horario que no existe para la actividad
        resultado = self.servicio.inscribir(
            nombre_actividad="Tirolesa",
            horario="22:00",  # no creado en setUp
            participantes=[participante],
            aceptar_terminos=True
        )

        self.assertFalse(resultado["exito"])
        # Mensaje del servicio: "Horario no disponible para la actividad."
        self.assertIn("horario", resultado["mensaje"].lower())


if __name__ == '__main__':
    unittest.main()
