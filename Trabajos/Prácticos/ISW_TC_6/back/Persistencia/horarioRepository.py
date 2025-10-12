from typing import Optional, Dict, List, Any
from Persistencia.databaseSingleton import DatabaseSingleton

class HorarioRepo:
    def __init__(self, db: DatabaseSingleton = None):
        self.db = db or DatabaseSingleton()

    def obtener_por_actividad_y_hora(self, actividad_id: int, hora: str) -> Optional[Dict[str, Any]]:
        rows = self.db.fetch_query(
            "SELECT id, hora, cupos FROM horario WHERE actividad_id = ? AND hora = ?",
            (actividad_id, hora)
        )
        if not rows:
            return None
        r = rows[0]
        return {"id": r["id"], "hora": r["hora"], "cupos": r["cupos"]}

    def listar_por_actividad(self, actividad_id: int) -> List[Dict[str, Any]]:
        rows = self.db.fetch_query("SELECT id, hora, cupos FROM horario WHERE actividad_id = ?", (actividad_id,))
        return [{"id": r["id"], "hora": r["hora"], "cupos": r["cupos"]} for r in rows] if rows else []

    def crear(self, actividad_id: int, hora: str, cupos: int) -> int:
        cur = self.db.execute_query("INSERT INTO horario (actividad_id, hora, cupos) VALUES (?, ?, ?)", (actividad_id, hora, cupos))
        return cur.lastrowid

    def decrementar_cupos(self, horario_id: int, cantidad: int):
        self.db.execute_query("UPDATE horario SET cupos = cupos - ? WHERE id = ?", (cantidad, horario_id))
