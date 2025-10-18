# cargaDatos.py
from databaseSingleton import DatabaseSingleton

class CargaDatos:
    def __init__(self):
        self.db = DatabaseSingleton()

    def _ensure_actividad_columns(self):
        """
        Verifica si las columnas 'descripcion' y 'terms' existen en la tabla 'actividad'.
        Si faltan, las agrega (SQLite permite ALTER TABLE ADD COLUMN).
        """
        # PRAGMA table_info devuelve filas tipo (cid, name, type, notnull, dflt_value, pk)
        cols = [row[1] for row in self.db.fetch_query("PRAGMA table_info(actividad)")]
        if "descripcion" not in cols:
            self.db.execute_query("ALTER TABLE actividad ADD COLUMN descripcion TEXT DEFAULT ''")
        if "terms" not in cols:
            self.db.execute_query("ALTER TABLE actividad ADD COLUMN terms TEXT DEFAULT ''")

    def cargar_actividades_y_horarios(self):
        # Asegurarnos que las columnas existan (para compatibilidad con DB previas)
        self._ensure_actividad_columns()

        # --- Actividades (nombre, requiere_talle, descripcion, terms) ---
        actividades = [
            ("Tirolesa", 1,
             "Deslízate por las copas de los árboles en una aventura emocionante.",
             "Los participantes deben tener al menos 12 años y pesar menos de 120kg. Se requiere calzado cerrado y ropa cómoda. El equipo de seguridad será proporcionado por el parque."),
            ("Safari", 0,
             "Recorre el parque en vehículo y conoce a nuestros animales de cerca.",
             "No se permite alimentar a los animales. Los niños menores de 5 años deben ir acompañados de un adulto. Se recomienda llevar protector solar y sombrero."),
            ("Palestra", 0,
             "Desafía tus habilidades en nuestro muro de escalada natural.",
             "Edad mínima 10 años. Se proporcionará todo el equipo de seguridad. Los participantes deben firmar un formulario de consentimiento."),
            ("Jardineria", 0,
             "Aprende sobre plantas nativas y ayuda en nuestro jardín botánico.",
             "Actividad apta para todas las edades. Se recomienda usar ropa que pueda ensuciarse. Se proporcionarán guantes y herramientas.")
        ]

        for nombre, requiere_talle, descripcion, terms in actividades:
            # Inserta si no existe
            self.db.execute_query(
                "INSERT OR IGNORE INTO actividad (nombre, requiere_talle) VALUES (?, ?)",
                (nombre, requiere_talle)
            )
            # Actualiza/asegura descripción y terms (si ya existía la fila)
            self.db.execute_query(
                "UPDATE actividad SET requiere_talle = ?, descripcion = ?, terms = ? WHERE nombre = ?",
                (requiere_talle, descripcion, terms, nombre)
            )

        # Obtener los IDs de cada actividad (según tu método fetch_query devuelve filas tipo tupla)
        act_tirolesa = self.db.fetch_query("SELECT id FROM actividad WHERE nombre = ?", ("Tirolesa",))[0][0]
        act_safari = self.db.fetch_query("SELECT id FROM actividad WHERE nombre = ?", ("Safari",))[0][0]
        act_palestra = self.db.fetch_query("SELECT id FROM actividad WHERE nombre = ?", ("Palestra",))[0][0]
        act_jardineria = self.db.fetch_query("SELECT id FROM actividad WHERE nombre = ?", ("Jardineria",))[0][0]

        # --- Horarios ---
        horarios = [
            # Tirolesa
            (act_tirolesa, "10:00", 10),
            (act_tirolesa, "12:00", 8),
            (act_tirolesa, "15:00", 6),

            # Safari
            (act_safari, "09:30", 12),
            (act_safari, "11:30", 10),
            (act_safari, "14:30", 8),

            # Palestra
            (act_palestra, "10:15", 5),
            (act_palestra, "13:00", 7),
            (act_palestra, "16:00", 6),

            # Jardineria
            (act_jardineria, "14:15", 6),
            (act_jardineria, "12:30", 9),
            (act_jardineria, "19:00", 11)
        ]

        for act_id, hora, cupos in horarios:
            self.db.execute_query(
                "INSERT OR IGNORE INTO horario (actividad_id, hora, cupos) VALUES (?, ?, ?)",
                (act_id, hora, cupos)
            )

        print("✅ Actividades, descripciones, términos y horarios cargados correctamente")


if __name__ == "__main__":
    CargaDatos().cargar_actividades_y_horarios()
