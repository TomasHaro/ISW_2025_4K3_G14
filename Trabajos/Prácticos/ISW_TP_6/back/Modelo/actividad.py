# models.py
from typing import List, Dict, Tuple
from Modelo.participante import Participante

class Actividad:
    def __init__(self, nombre: str, horarios: List[str], cupos_por_horario: Dict[str, int], requiere_talle: bool):
        self.nombre = nombre
        self.horarios = horarios
        self.cupos_por_horario = cupos_por_horario.copy()
        self.requiere_talle = requiere_talle
        # inscripciones será lista de tuplas (horario, participante)
        self.inscripciones: List[Tuple[str, Participante]] = []

    def tiene_cupo(self, horario: str, cantidad: int = 1) -> bool:
        """Devuelve True si hay al menos "cantidad" cupos para el horario dado."""
        return self.cupos_por_horario.get(horario, 0) >= cantidad

    def registrar_inscripciones(self, horario: str, visitantes: List[Participante]) -> bool:
        """
        Registra varias inscripciones de forma atómica:
        - Si no hay cupo suficiente devuelve False y no cambia estado.
        - Si hay cupo suficiente decrementa y registra, devuelve True.
        """
        cantidad = len(visitantes)
        disponibles = self.cupos_por_horario.get(horario, 0)
        if disponibles < cantidad:
            return False
        # decrementar y agregar
        self.cupos_por_horario[horario] = disponibles - cantidad
        for v in visitantes:
            self.inscripciones.append((horario, v))
        return True
