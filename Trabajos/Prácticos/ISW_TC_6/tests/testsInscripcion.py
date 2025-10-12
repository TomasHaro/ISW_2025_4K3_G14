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

if __name__ == '__main__':
    unittest.main()

