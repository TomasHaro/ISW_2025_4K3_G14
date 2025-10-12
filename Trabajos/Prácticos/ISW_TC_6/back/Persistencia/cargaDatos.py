from databaseSingleton import DatabaseSingleton

class CargaDatos:
    def __init__(self):
        self.db = DatabaseSingleton()

    def cargar_actividades_y_horarios(self):
        # Actividades
        actividades = [
            ("Tirolesa", 1),
            ("Safari", 0),
            ("Palestra", 0),
            ("Jardinería", 0)
        ]
        for nombre, requiere_talle in actividades:
            self.db.execute_query(
                "INSERT OR IGNORE INTO actividad (nombre, requiere_talle) VALUES (?, ?)",
                (nombre, requiere_talle)
            )

        # Horarios
        act_tirolesa = self.db.fetch_query("SELECT id FROM actividad WHERE nombre = ?", ("Tirolesa",))[0][0]
        act_safari = self.db.fetch_query("SELECT id FROM actividad WHERE nombre = ?", ("Safari",))[0][0]

        horarios = [
            (act_tirolesa, "10:00", 5),
            (act_tirolesa, "12:00", 3),
            (act_safari, "15:00", 0)
        ]
        for act_id, hora, cupos in horarios:
            self.db.execute_query(
                "INSERT OR IGNORE INTO horario (actividad_id, hora, cupos) VALUES (?, ?, ?)",
                (act_id, hora, cupos)
            )
        print("✅ Datos de ejemplo cargados")
