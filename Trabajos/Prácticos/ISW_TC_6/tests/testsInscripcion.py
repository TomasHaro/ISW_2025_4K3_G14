import unittest
from Persistencia.databaseSingleton import DatabaseSingleton
from Persistencia.actividadRepository import ActividadRepo
from Persistencia.horarioRepository import HorarioRepo
from Persistencia.participanteRepository import ParticipanteRepo
from Persistencia.inscripcionRepository import InscripcionRepo
from Servicio.inscripcionServicio import InscripcionService
from Modelo.participante import Participante

class TestInscripcionActividadDB(unittest.TestCase):
    def setUp(self):
        # Usamos DB en memoria para tests aislados
        self.db = DatabaseSingleton(":memory:")
        # repositorios y servicio apuntando a la misma DB en memoria
        self.actividad_repo = ActividadRepo(self.db)
        self.horario_repo = HorarioRepo(self.db)
        self.inscripcion_repo = InscripcionRepo(self.db)
        self.servicio = InscripcionService(db=self.db)

        # Poblar datos necesarios para los tests
        # Actividad Tirolesa (requiere talle) con horarios 10:00 (5 cupos) y 12:00 (5 cupos)
        self.aid_tirolesa = self.actividad_repo.crear("Tirolesa", True)
        self.horario_repo.crear(self.aid_tirolesa, "10:00", 5)
        self.horario_repo.crear(self.aid_tirolesa, "12:00", 5)

        # Actividad Safari (no requiere talle) con horario 15:00 (0 cupos) para prueba de falla
        self.aid_safari = self.actividad_repo.crear("Safari", False)
        self.horario_repo.crear(self.aid_safari, "15:00", 0)

        # Actividad Jardinería (no requiere talle) con horario 11:00 (3 cupos)
        self.aid_jard = self.actividad_repo.crear("Jardinería", False)
        self.horario_repo.crear(self.aid_jard, "11:00", 3)

    def tearDown(self):
        # Cerrar conexión y eliminar instancia del singleton para asegurar aislamiento
        self.db.close_connection()

    # Happy path
    def test_inscripcion_exitosa_con_terminos_aceptados(self):
        participante = Participante(nombre="Juan", dni="12345678", edad=25, talle="M")

        resultado = self.servicio.inscribir(
            nombre_actividad="Tirolesa",
            horario="10:00",
            participantes=[participante],
            aceptar_terminos=True
        )

        self.assertTrue(resultado["exito"])
        self.assertEqual(resultado["mensaje"], "Inscripción realizada con éxito.")
        # Verificar que el cupo en DB se decrementó
        h = self.horario_repo.obtener_por_actividad_y_hora(self.aid_tirolesa, "10:00")
        self.assertEqual(h["cupos"], 4)
        # Verificar que hay una inscripcion registrada para ese horario
        inscripciones = self.inscripcion_repo.listar_por_horario(h["id"])
        self.assertEqual(len(inscripciones), 1)
        self.assertEqual(inscripciones[0]["dni"], "12345678")

    # Probar inscribirse a una actividad sin cupo para un horario (falla)
    def test_inscripcion_falla_cuando_no_hay_cupo_en_el_horario(self):
        participante = Participante(nombre="María", dni="33333333", edad=30, talle=None)

        resultado = self.servicio.inscribir(
            nombre_actividad="Safari",
            horario="15:00",
            participantes=[participante],
            aceptar_terminos=True
        )

        self.assertFalse(resultado["exito"])
        # Mensaje informando falta de cupos (no dependemos del texto exacto)
        self.assertIn("cupos", resultado["mensaje"].lower())

        # Verificar que el cupo sigue en 0 y no se registraron inscripciones
        h = self.horario_repo.obtener_por_actividad_y_hora(self.aid_safari, "15:00")
        self.assertEqual(h["cupos"], 0)
        inscripciones = self.inscripcion_repo.listar_por_horario(h["id"])
        self.assertEqual(len(inscripciones), 0)

    # Probar inscribirse a una actividad sin ingresar talle cuando NO se requiere (pasa)
    def test_inscripcion_exitosa_sin_talle_cuando_no_se_requiere(self):
        participante = Participante(nombre="Laura", dni="22222222", edad=28, talle=None)

        resultado = self.servicio.inscribir(
            nombre_actividad="Jardinería",
            horario="11:00",
            participantes=[participante],
            aceptar_terminos=True
        )

        self.assertTrue(resultado["exito"])
        self.assertEqual(resultado["mensaje"], "Inscripción realizada con éxito.")
        h = self.horario_repo.obtener_por_actividad_y_hora(self.aid_jard, "11:00")
        self.assertEqual(h["cupos"], 2)
        inscripciones = self.inscripcion_repo.listar_por_horario(h["id"])
        self.assertEqual(len(inscripciones), 1)
        self.assertEqual(inscripciones[0]["dni"], "22222222")

if __name__ == '__main__':
    unittest.main()
