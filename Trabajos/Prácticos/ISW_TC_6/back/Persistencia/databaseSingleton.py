# Servicio/databaseSingleton.py
import sqlite3
from sqlite3 import Error
from typing import Optional
import os

class DatabaseSingleton:
    """
    Singleton por ruta de DB. Llamar DatabaseSingleton(db_path) devuelve la instancia única para ese db_path.
    Útil para tests: DatabaseSingleton(':memory:') crea/usa una DB en memoria separada.
    """
    _instances = {}

    def __new__(cls, db_path: str = "ecoharmony.db"):
        if db_path not in cls._instances:
            inst = super().__new__(cls)
            cls._instances[db_path] = inst
            inst._db_path = db_path
            inst._initialize_connection()
        return cls._instances[db_path]

    def _initialize_connection(self):
        try:
            self.connection = sqlite3.connect(self._db_path, timeout=30, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            # Inicializar/crear tablas y columnas necesarias
            self._initialize_database()
        except Error as e:
            raise RuntimeError(f"Error al conectar a la base de datos: {e}")

    def _initialize_database(self):
        try:
            # Creamos la tabla actividad con las columnas nuevas descripcion y terms (por defecto '')
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS actividad (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    requiere_talle INTEGER NOT NULL,
                    descripcion TEXT DEFAULT '',
                    terms TEXT DEFAULT ''
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
                    dni TEXT NOT NULL UNIQUE,
                    edad INTEGER NOT NULL,
                    talle TEXT
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS inscripcion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    participante_id INTEGER NOT NULL,
                    horario_id INTEGER NOT NULL,
                    acepta_terminos INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(participante_id) REFERENCES participante(id),
                    FOREIGN KEY(horario_id) REFERENCES horario(id)
                )
            """)
            # Asegurarnos (compatibilidad) de que si la tabla actividad existía y le faltan
            # las columnas nuevas, las agregamos con ALTER TABLE (SQLite permite ADD COLUMN).
            self._ensure_actividad_columns()
            self.connection.commit()
        except Error as e:
            raise RuntimeError(f"Error al crear/verificar las tablas: {e}")

    def _ensure_actividad_columns(self):
        """
        Comprueba columnas en actividad y agrega las que falten: descripcion, terms.
        Esto permite compatibilidad con esquemas antiguos.
        """
        try:
            cur = self.connection.cursor()
            cur.execute("PRAGMA table_info(actividad)")
            cols = [row[1] for row in cur.fetchall()]  # row: (cid, name, type, notnull, dflt_value, pk)
            if "descripcion" not in cols:
                cur.execute("ALTER TABLE actividad ADD COLUMN descripcion TEXT DEFAULT ''")
            if "terms" not in cols:
                cur.execute("ALTER TABLE actividad ADD COLUMN terms TEXT DEFAULT ''")
        except Error:
            # Si por alguna razón falla (p. ej. tabla no existe aún), no hacemos nada especial aquí;
            # el CREATE TABLE anterior ya maneja la creación para DB nuevas.
            pass

    # helpers
    def execute_query(self, query: str, parameters: tuple = ()):
        try:
            cur = self.connection.cursor()
            cur.execute(query, parameters)
            self.connection.commit()
            return cur
        except Error as e:
            # re-lanzamos la excepción (podés personalizar el logging aquí)
            raise

    def fetch_query(self, query: str, parameters: tuple = ()):
        try:
            cur = self.connection.cursor()
            cur.execute(query, parameters)
            return cur.fetchall()
        except Error as e:
            raise

    def close_connection(self):
        if getattr(self, "connection", None):
            self.connection.close()
            # opcional: eliminar instancia del mapa para permitir recrear la DB en memoria en tests
            if self._db_path in DatabaseSingleton._instances:
                del DatabaseSingleton._instances[self._db_path]
