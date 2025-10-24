from typing import List, Dict, Any
from Persistencia.database_singleton import DatabaseSingleton

class InscripcionRepo:
    def __init__(self, db: DatabaseSingleton = None):
        self.db = db or DatabaseSingleton()

    def crear_inscripcion(self, participante_id: int, horario_id: int, acepta_terminos: bool) -> int:
        cur = self.db.execute_query(
            "INSERT INTO inscripcion (participante_id, horario_id, acepta_terminos) VALUES (?, ?, ?)",
            (participante_id, horario_id, 1 if acepta_terminos else 0)
        )
        return cur.lastrowid

    def listar_por_horario(self, horario_id: int) -> List[Dict[str, Any]]:
        rows = self.db.fetch_query(
            """SELECT i.id, p.nombre, p.dni, p.edad, p.talle, i.acepta_terminos
               FROM inscripcion i
               JOIN participante p ON p.id = i.participante_id
               WHERE i.horario_id = ?""",
            (horario_id,)
        )
        result = []
        for r in rows:
            result.append({
                "inscripcion_id": r["id"],
                "nombre": r["nombre"],
                "dni": r["dni"],
                "edad": r["edad"],
                "talle": r["talle"],
                "acepta_terminos": bool(r["acepta_terminos"])
            })
        return result
