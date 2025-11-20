# Persistencia/actividadRepository.py
from typing import Optional, Dict, List, Any
from Persistencia.database_singleton import DatabaseSingleton

class ActividadRepo:
    def __init__(self, db: DatabaseSingleton = None):
        self.db = db or DatabaseSingleton()

    def _row_to_dict(self, r) -> Dict[str, Any]:
        # r puede ser sqlite3.Row (accesible por nombre) o tuple (accesible por index)
        try:
            # sqlite3.Row o dict-like
            return {
                "id": r["id"],
                "nombre": r["nombre"],
                "requiere_talle": bool(r["requiere_talle"]),
                "descripcion": r.get("descripcion", "") if hasattr(r, "keys") else r["descripcion"],
                "terms": r.get("terms", "") if hasattr(r, "keys") else r["terms"]
            }
        except Exception:
            # fallback para tuple (orden: id, nombre, requiere_talle, descripcion, terms)
            return {
                "id": r[0],
                "nombre": r[1],
                "requiere_talle": bool(r[2]),
                "descripcion": r[3] if len(r) > 3 else "",
                "terms": r[4] if len(r) > 4 else ""
            }

    def obtener_por_nombre(self, nombre: str) -> Optional[Dict[str, Any]]:
        rows = self.db.fetch_query(
            "SELECT id, nombre, requiere_talle, descripcion, terms FROM actividad WHERE nombre = ?",
            (nombre,)
        )
        if not rows:
            return None
        return self._row_to_dict(rows[0])

    def listar_todas(self) -> List[Dict[str, Any]]:
        rows = self.db.fetch_query("SELECT id, nombre, requiere_talle, descripcion, terms FROM actividad")
        if not rows:
            return []
        return [self._row_to_dict(r) for r in rows]

    def crear(self, nombre: str, requiere_talle: bool, descripcion: str = "", terms: str = "") -> int:
        cur = self.db.execute_query(
            "INSERT OR IGNORE INTO actividad (nombre, requiere_talle, descripcion, terms) VALUES (?, ?, ?, ?)",
            (nombre, 1 if requiere_talle else 0, descripcion, terms)
        )
        if cur.lastrowid:
            return cur.lastrowid
        row = self.db.fetch_query("SELECT id FROM actividad WHERE nombre = ?", (nombre,))
        return row[0][0] if row else None
