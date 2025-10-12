import unittest
from Modelo.actividad import Actividad
from Modelo.participante import Participante
from Servicio.inscripcionServicio import InscripcionServicio

class TestInscripcionActividad(unittest.TestCase):
    def setUp(self):
        # Configuramos una actividad con cupos y horarios
        self.actividad = Actividad(
            nombre="Tirolesa",
            horarios=["10:00", "12:00"],
            cupos_por_horario={"10:00": 5, "12:00": 5},
            requiere_talle=True
        )

        self.servicio = InscripcionServicio([self.actividad])

    # Happy path
    def test_inscripcion_exitosa_con_terminos_aceptados(self):
        # Creamos un participante con datos completos
        participante = Participante(
            nombre="Juan",
            dni="12345678",
            edad=25,
            talle="M"
        )

        # Intentamos inscribir al visitante
        resultado = self.servicio.inscribir(
            nombre_actividad="Tirolesa",
            horario="10:00",
            participantes=[participante],
            aceptar_terminos=True  
        )

        # Verificamos el resultado
        self.assertTrue(resultado["exito"])
        self.assertEqual(resultado["mensaje"], "Inscripción realizada con éxito.")
        self.assertEqual(self.actividad.cupos_por_horario["10:00"], 4)  # cupo disminuye

    # Probar inscribirse a una actividad sin cupo para un horario
    def test_inscripcion_falla_cuando_no_hay_cupo_en_el_horario(self):
        # Configuro una actividad con 0 cupos en el horario solicitado
        actividad = Actividad(
            nombre="Safari",
            horarios=["15:00"],
            cupos_por_horario={"15:00": 0},  # sin cupos
            requiere_talle=False
        )
        servicio = InscripcionServicio([actividad])

        participante = Participante(nombre="María", dni="33333333", edad=30, talle=None)

        resultado = servicio.inscribir(
            nombre_actividad="Safari",
            horario="15:00",
            participantes=[participante],
            aceptar_terminos=True
        )

        # Debe fallar la inscripción
        self.assertFalse(resultado["exito"])
        # Mensaje informando falta de cupos (ajusta el texto si tu implementación usa otro)
        self.assertIn("cupos", resultado["mensaje"].lower())

        # Estado inmutable: el cupo sigue en 0 y no se registraron inscripciones
        self.assertEqual(actividad.cupos_por_horario["15:00"], 0)
        self.assertEqual(len(actividad.inscripciones), 0)

    # Probar inscribirse a una actividad sin ingresar talle de vestimenta porque la actividad no lo requiere
    def test_inscripcion_exitosa_sin_talle_cuando_no_se_requiere(self):
        # Configuramos una actividad que NO requiere talle
        actividad = Actividad(
            nombre="Jardinería",
            horarios=["11:00"],
            cupos_por_horario={"11:00": 3},
            requiere_talle=False
        )

        servicio = InscripcionServicio([actividad])

        # Creamos un participante SIN talle
        participante = Participante(
            nombre="Laura",
            dni="22222222",
            edad=28,
            talle=None
        )

        # Intentamos inscribir al participante
        resultado = servicio.inscribir(
            nombre_actividad="Jardinería",
            horario="11:00",
            participantes=[participante],
            aceptar_terminos=True
        )

        self.assertTrue(resultado["exito"])
        self.assertEqual(resultado["mensaje"], "Inscripción realizada con éxito.")
        self.assertEqual(actividad.cupos_por_horario["11:00"], 2)  # Se reduce el cupo
        self.assertEqual(len(actividad.inscripciones), 1)

if __name__ == '__main__':
    unittest.main()

