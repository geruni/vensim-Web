import os
import sqlite3

from decouple import config, UndefinedValueError

# Ruta por defecto de la BD SQLite: vensimweb_sjl/db/vensimweb_sjl.db
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DB_PATH_DEFECTO = os.path.join(_BASE_DIR, 'db', 'vensimweb_sjl.db')


def _dict_factory(cursor, row):
    """Convierte cada fila en un dict real (soporta .get() e item-asignacion,
    igual que el `cursor(dictionary=True)` de mysql-connector)."""
    return {col[0]: value for col, value in zip(cursor.description, row)}


class _SQLiteConnection:
    """Envoltura minima sobre sqlite3.Connection para exponer la misma API
    que usa el resto del codigo (heredada de mysql-connector): cursor(dictionary=...),
    commit(), close()."""

    def __init__(self, conn):
        self._conn = conn

    def cursor(self, dictionary=False):
        self._conn.row_factory = _dict_factory if dictionary else None
        return self._conn.cursor()

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def connect():
    """
    Abre conexion con la base de datos SQLite (archivo local).
    Retorna objeto conexion si tiene exito, o diccionario con error.
    """
    try:
        db_path = config('DB_PATH', default=_DB_PATH_DEFECTO)
    except UndefinedValueError:
        db_path = _DB_PATH_DEFECTO

    if not os.path.isfile(db_path):
        return {'error': f'No se encontro la base de datos SQLite en "{db_path}". '
                          f'Ejecuta "python db/init_db.py" para crearla.'}
    try:
        conn = sqlite3.connect(db_path)
        conn.execute('PRAGMA foreign_keys = ON')
        return _SQLiteConnection(conn)
    except Exception:
        return {'error': 'No se pudo conectar a la base de datos SQLite.'}


def connection_select(cursorObject, select_stmt, params=None):
    """
    Ejecuta una consulta SELECT y retorna los resultados.
    Traduce los placeholders %s (estilo MySQL, usados en el resto del codigo)
    a ? (estilo sqlite3).
    """
    cursorObject.execute(select_stmt.replace('%s', '?'), params or ())
    return cursorObject.fetchall()


def connection_execute(cursorObject, stmt, params=None):
    """
    Ejecuta una sentencia de escritura (INSERT/UPDATE/DELETE).
    El commit lo maneja la conexion que invoca esta funcion.
    """
    cursorObject.execute(stmt.replace('%s', '?'), params or ())
    return cursorObject
