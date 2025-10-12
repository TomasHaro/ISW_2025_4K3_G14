# servicio.py
from typing import List, Dict, Any
from Modelo.participante import Participante
from Modelo.actividad import Actividad

class InscripcionServicio:
    def __init__(self, actividades: List[Actividad]):
        # mapear por nombre
        self.actividades = {a.nombre: a for a in actividades}

    def inscribir(self, nombre_actividad: str, horario: str, participantes: List[Participante], aceptar_terminos: bool) -> Dict[str, Any]:
        """
        Realiza la inscripción cumpliendo los criterios:
        - actividad existente
        - horario disponible para la actividad
        - aceptar_terminos == True
        - validar datos por participante (talle si corresponde)
        - cupo suficiente para la cantidad de participantes
        - operación atómica: o todo se registra o nada
        """
        actividad = self.actividades.get(nombre_actividad)
        if not actividad:
            return {"exito": False, "mensaje": "Actividad no encontrada."}

        if horario not in actividad.horarios:
            return {"exito": False, "mensaje": "Horario no disponible para la actividad."}

        if not aceptar_terminos:
            return {"exito": False, "mensaje": "Debe aceptar los términos y condiciones para inscribirse."}

        if not participantes or len(participantes) == 0:
            return {"exito": False, "mensaje": "Debe indicar al menos un participante."}

        # validar campos de cada participante
        for p in participantes:
            if not getattr(p, "nombre", None) or not getattr(p, "dni", None) or not getattr(p, "edad", None):
                return {"exito": False, "mensaje": "Datos de participante incompletos."}
            if actividad.requiere_talle and not getattr(p, "talle", None):
                return {"exito": False, "mensaje": "Talle requerido para la actividad."}

        # comprobar cupo (cantidad)
        cantidad = len(participantes)
        if not actividad.tiene_cupo(horario, cantidad):
            return {"exito": False, "mensaje": "No hay cupos suficientes para ese horario."}

        # registrar de forma atómica
        ok = actividad.registrar_inscripciones(horario, participantes)
        if not ok:
            return {"exito": False, "mensaje": "No se pudo completar la inscripción (cupo insuficiente)."}

        return {"exito": True, "mensaje": "Inscripción realizada con éxito."}
