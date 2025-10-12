class Inscripcion:
    def inscribir(self, actividad, nombre, dni, edad, talla=None, acepta_terminos=False):
        if not acepta_terminos:
            return False
        if len(actividad.participantes) >= actividad.cupo_maximo:
            return False
        actividad.participantes.append({
            "nombre": nombre,
            "dni": dni,
            "edad": edad,
            "talla": talla
        })
        return True
