from typing import Optional, Dict, List, Any
from Persistencia.databaseSingleton import DatabaseSingleton

class ActividadRepo:
    def __init__(self, db: DatabaseSingleton = None):
        self.db = db or DatabaseSingleton()

    def obtener_por_nombre(self, nombre: str) -> Optional[Dict[str, Any]]:
        rows = self.db.fetch_query("SELECT id, nombre, requiere_talle FROM actividad WHERE nombre = ?", (nombre,))
        if not rows:
            return None
        r = rows[0]
        return {"id": r["id"], "nombre": r["nombre"], "requiere_talle": bool(r["requiere_talle"])}

    def listar_todas(self) -> List[Dict[str, Any]]:
        rows = self.db.fetch_query("SELECT id, nombre, requiere_talle FROM actividad")
        return [{"id": r["id"], "nombre": r["nombre"], "requiere_talle": bool(r["requiere_talle"])} for r in rows] if rows else []

    def crear(self, nombre: str, requiere_talle: bool) -> int:
        cur = self.db.execute_query(
            "INSERT OR IGNORE INTO actividad (nombre, requiere_talle) VALUES (?, ?)",
            (nombre, 1 if requiere_talle else 0)
        )
        return cur.lastrowid
