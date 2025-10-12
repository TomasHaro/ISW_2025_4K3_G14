class InscripcionServicio:
    def __init__(self, actividades):
        self.actividades = {a.nombre: a for a in actividades}

    def inscribir(self, nombre_actividad, horario, participantes, aceptar_terminos):
        actividad = self.actividades.get(nombre_actividad)

        # Implementación mínima para pasar el caso feliz
        if not actividad:
            return {"exito": False, "mensaje": "Actividad no encontrada."}

        if not aceptar_terminos:
            return {"exito": False, "mensaje": "Debe aceptar los términos y condiciones para inscribirse."}

        if not actividad.tiene_cupo(horario):
            return {"exito": False, "mensaje": "No hay cupos disponibles para este horario."}

        for v in participantes:
            actividad.registrar_inscripcion(horario, v)

        return {"exito": True, "mensaje": "Inscripción realizada con éxito."}
