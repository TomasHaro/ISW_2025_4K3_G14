from databaseSingleton import DatabaseSingleton
from cargaDatos import CargaDatos

# Inicializa la base de datos
db = DatabaseSingleton()

# Carga datos de ejemplo
carga = CargaDatos()
carga.cargar_actividades_y_horarios()
