from Persistencia.database_singleton import DatabaseSingleton
from Persistencia.carga_datos import CargaDatos

# Inicializa la base de datos
db = DatabaseSingleton()

# Carga datos de ejemplo
carga = CargaDatos()
carga.cargar_actividades_y_horarios()
