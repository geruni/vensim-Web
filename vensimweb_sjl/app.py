import os

from flask import Flask

from db.init_db import ensure_db
from src.Routes.route import routes

# Crea la base de datos SQLite si todavía no existe (no la sobreescribe).
ensure_db()

# Crear aplicación Flask
app = Flask(__name__)

# Registrar rutas
app.register_blueprint(routes)

if __name__ == '__main__':
    # Uso local / desarrollo. En producción (Render) se usa gunicorn (ver Procfile),
    # que importa la variable `app` de este módulo directamente.
    port = int(os.environ.get('PORT', 5000))
    print(' * Starting Flask app...')
    app.run(host='0.0.0.0', port=port, debug=False)
