from typing import Optional
from Persistencia.databaseSingleton import DatabaseSingleton

class ParticipanteRepo:
    def __init__(self, db: DatabaseSingleton = None):
        self.db = db or DatabaseSingleton()

    def obtener_por_dni(self, dni: str) -> Optional[int]:
        rows = self.db.fetch_query("SELECT id FROM participante WHERE dni = ?", (dni,))
        return rows[0]["id"] if rows else None

    def crear(self, nombre: str, dni: str, edad: int, talle: str = None) -> int:
        cur = self.db.execute_query(
            "INSERT OR IGNORE INTO participante (nombre, dni, edad, talle) VALUES (?, ?, ?, ?)",
            (nombre, dni, edad, talle)
        )
        # si se usó INSERT OR IGNORE y ya existía, lastrowid puede ser 0 -> leer por dni
        if cur.lastrowid:
            return cur.lastrowid
        row = self.db.fetch_query("SELECT id FROM participante WHERE dni = ?", (dni,))
        return row[0]["id"]
