"""
Crea (o recrea) la base de datos SQLite del proyecto a partir de db/schema.sql.

Se usa de dos formas:
  1. Como "Build Command" en Render: `python db/init_db.py --force`
     (siempre deja una base de datos limpia con la config/datos reales de fábrica
     en cada deploy; los escenarios guardados por usuarios no persisten entre
     deploys porque el disco del free tier de Render es efímero).
  2. Importado desde app.py al arrancar: `ensure_db()` sin --force, para que
     un entorno local o un restart sin rebuild también tengan la BD lista.
"""
import os
import sqlite3
import argparse

from decouple import config, UndefinedValueError

_HERE = os.path.dirname(os.path.abspath(__file__))
_SCHEMA_PATH = os.path.join(_HERE, 'schema.sql')
_DEFAULT_DB_PATH = os.path.join(_HERE, 'vensimweb_sjl.db')


def _resolver_db_path(db_path=None):
    if db_path:
        return db_path
    try:
        return config('DB_PATH', default=_DEFAULT_DB_PATH)
    except UndefinedValueError:
        return _DEFAULT_DB_PATH


def ensure_db(db_path=None, force=False):
    """
    Crea el archivo SQLite y su esquema si no existe (o si force=True lo recrea
    desde cero). Retorna la ruta final del archivo .db.
    """
    ruta = _resolver_db_path(db_path)

    if os.path.isfile(ruta):
        if not force:
            return ruta
        os.remove(ruta)

    os.makedirs(os.path.dirname(ruta) or '.', exist_ok=True)

    with open(_SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    conn = sqlite3.connect(ruta)
    try:
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()

    return ruta


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Inicializa la base de datos SQLite de vensimweb_sjl.')
    parser.add_argument('--force', action='store_true',
                         help='Recrea la base de datos aunque ya exista.')
    parser.add_argument('--db-path', default=None,
                         help='Ruta del archivo .db (por defecto: db/vensimweb_sjl.db, '
                              'o la variable de entorno DB_PATH).')
    args = parser.parse_args()

    ruta_final = ensure_db(db_path=args.db_path, force=args.force)
    print(f'Base de datos lista en: {ruta_final}')
