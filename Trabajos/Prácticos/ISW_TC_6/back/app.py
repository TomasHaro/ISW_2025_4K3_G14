# backend/app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from Persistencia.database_singleton import DatabaseSingleton
from Persistencia.actividad_repository import ActividadRepo
from Persistencia.horario_repository import HorarioRepo
from Servicio.inscripcion_servicio import InscripcionService 

app = FastAPI()  # NO usar prefix aquí

# Orígenes permitidos (añadí localhost:3000 para Next y 5173 para Vite; en producción reemplazar por tu dominio)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar DB
DB_PATH = "ecoharmony.db"
db = DatabaseSingleton(DB_PATH)

actividad_repo = ActividadRepo(db)
horario_repo = HorarioRepo(db)
servicio = InscripcionService(db=db)

# Pydantic models
class ParticipanteIn(BaseModel):
    nombre: str
    dni: str
    edad: int
    talle: Optional[str] = None

class InscripcionIn(BaseModel):
    nombre_actividad: str
    horario: str
    participantes: List[ParticipanteIn]
    aceptar_terminos: bool

@app.get("/api/actividades")
def listar_actividades():
    """
    Devuelve lista de actividades con id, nombre, requiere_talle, descripcion, terms
    """
    rows = actividad_repo.listar_todas()
    # Aseguramos los campos (por si el repo antiguo no incluye descripcion/terms)
    result = []
    for r in rows:
        result.append({
            "id": r.get("id"),
            "nombre": r.get("nombre"),
            "requiere_talle": bool(r.get("requiere_talle", False)),
            "descripcion": r.get("descripcion", "") if isinstance(r, dict) else "",
            "terms": r.get("terms", "") if isinstance(r, dict) else "",
        })
    return result

@app.get("/api/actividades/{actividad_id}/horarios")
def listar_horarios(actividad_id: int):
    """
    Devuelve los horarios (id, hora, cupos) para una actividad
    """
    return horario_repo.listar_por_actividad(actividad_id)

@app.post("/api/inscripciones")
def crear_inscripcion(payload: InscripcionIn):
    # Construir objetos Participante esperados por el servicio
    participantes = []
    from Modelo.participante import Participante
    for p in payload.participantes:
        participantes.append(Participante(p.nombre, p.dni, p.edad, p.talle))
    res = servicio.inscribir(payload.nombre_actividad, payload.horario, participantes, payload.aceptar_terminos)
    if not res.get("exito", False):
        raise HTTPException(status_code=400, detail=res.get("mensaje", "Error"))
    return res

@app.get("/api/health")
def health():
    return {"ok": True}
