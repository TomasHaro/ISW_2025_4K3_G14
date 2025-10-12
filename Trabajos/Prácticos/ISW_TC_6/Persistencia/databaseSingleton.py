import sqlite3
from sqlite3 import Error
import os

class DatabaseSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseSingleton, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance

    def _initialize_connection(self):
        try:
            # Conexión a la base de datos
            self.connection = sqlite3.connect("ecoharmony.db")
            self.cursor = self.connection.cursor()
            print("Conexión a SQLite establecida")
            
            # Inicializar la base de datos si es necesario
            self._initialize_database()
            
        except Error as e:
            print(f"Error al conectar a la base de datos: {e}")

    def _initialize_database(self):
        """Crea las tablas si no existen"""
        try:
            # Ajusta las tablas a tu modelo de EcoHarmony Park
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS actividad (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    requiere_talle BOOLEAN NOT NULL
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS horario (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    actividad_id INTEGER NOT NULL,
                    hora TEXT NOT NULL,
                    cupos INTEGER NOT NULL,
                    FOREIGN KEY(actividad_id) REFERENCES actividad(id)
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS participante (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    dni TEXT NOT NULL,
                    edad INTEGER NOT NULL,
                    talle TEXT
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS inscripcion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    participante_id INTEGER NOT NULL,
                    horario_id INTEGER NOT NULL,
                    acepta_terminos BOOLEAN NOT NULL,
                    FOREIGN KEY(participante_id) REFERENCES participante(id),
                    FOREIGN KEY(horario_id) REFERENCES horario(id)
                )
            """)
            self.connection.commit()
            print("Tablas creadas/verificadas correctamente")
        except Error as e:
            print(f"Error al crear/verificar las tablas: {e}")

    def execute_query(self, query, parameters=()):
        try:
            self.cursor.execute(query, parameters)
            self.connection.commit()
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")

    def fetch_query(self, query, parameters=()):
        try:
            self.cursor.execute(query, parameters)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error al obtener datos: {e}")
            return None

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            print("Conexión cerrada")

if __name__ == "__main__":
    db = DatabaseSingleton()
