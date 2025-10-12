from typing import List, Dict, Any
from Persistencia.databaseSingleton import DatabaseSingleton
from Persistencia.actividadRepository import ActividadRepo
from Persistencia.horarioRepository import HorarioRepo
from Persistencia.participanteRepository import ParticipanteRepo
from Persistencia.inscripcionRepository import InscripcionRepo
from Modelo.participante import Participante

class InscripcionService:
    def __init__(self, db: DatabaseSingleton = None):
        self.db = db or DatabaseSingleton()
        self.actividad_repo = ActividadRepo(self.db)
        self.horario_repo = HorarioRepo(self.db)
        self.participante_repo = ParticipanteRepo(self.db)
        self.inscripcion_repo = InscripcionRepo(self.db)

    def _validar_participante_basico(self, p: Participante) -> bool:
        return bool(getattr(p, "nombre", None) and getattr(p, "dni", None) and getattr(p, "edad", None))

    def inscribir(self, nombre_actividad: str, horario: str, participantes: List[Participante], aceptar_terminos: bool) -> Dict[str, Any]:
        act = self.actividad_repo.obtener_por_nombre(nombre_actividad)
        if not act:
            return {"exito": False, "mensaje": "Actividad no encontrada."}

        horario_row = self.horario_repo.obtener_por_actividad_y_hora(act["id"], horario)
        if not horario_row:
            return {"exito": False, "mensaje": "Horario no disponible para la actividad."}

        if not aceptar_terminos:
            return {"exito": False, "mensaje": "Debe aceptar los términos y condiciones para inscribirse."}

        if not participantes:
            return {"exito": False, "mensaje": "Debe indicar al menos un participante."}

        for p in participantes:
            if not self._validar_participante_basico(p):
                return {"exito": False, "mensaje": "Datos de participante incompletos."}
            if act["requiere_talle"] and not getattr(p, "talle", None):
                return {"exito": False, "mensaje": "Talle requerido para la actividad."}

        cantidad = len(participantes)

        conn = self.db.connection
        try:
            with conn:  # transacción
                cur = conn.cursor()
                cur.execute("SELECT cupos FROM horario WHERE id = ?", (horario_row["id"],))
                row = cur.fetchone()
                if not row:
                    return {"exito": False, "mensaje": "Horario no encontrado."}
                cupos_actuales = row["cupos"]
                if cupos_actuales < cantidad:
                    return {"exito": False, "mensaje": "No hay cupos suficientes para ese horario."}

                # registrar participantes e inscripciones
                for p in participantes:
                    pid = self.participante_repo.obtener_por_dni(p.dni)
                    if not pid:
                        pid = self.participante_repo.crear(p.nombre, p.dni, p.edad, p.talle)
                    self.inscripcion_repo.crear_inscripcion(pid, horario_row["id"], aceptar_terminos)

                # decrementar cupos
                self.horario_repo.decrementar_cupos(horario_row["id"], cantidad)

            return {"exito": True, "mensaje": "Inscripción realizada con éxito."}
        except Exception as e:
            return {"exito": False, "mensaje": f"Ocurrió un error al inscribir: {e}"}
