class Actividad:
    def __init__(self, nombre, horarios, cupos_por_horario, requiere_talle):
        self.nombre = nombre
        self.horarios = horarios
        self.cupos_por_horario = cupos_por_horario
        self.requiere_talle = requiere_talle
        self.inscripciones = []  # lista de visitantes inscriptos

    def tiene_cupo(self, horario):
        """Devuelve True si hay cupos disponibles para el horario dado."""
        return self.cupos_por_horario.get(horario, 0) > 0

    def registrar_inscripcion(self, horario, visitante):
        """Disminuye el cupo y registra al visitante."""
        if self.tiene_cupo(horario):
            self.cupos_por_horario[horario] -= 1
            self.inscripciones.append((horario, visitante))
