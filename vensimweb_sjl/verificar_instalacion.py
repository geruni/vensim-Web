"""
Script de verificación de instalación
Ejecuta este script antes de iniciar la aplicación para verificar que todo está configurado correctamente.
"""

import os


def verificar_archivo(ruta, descripcion):
    """Verifica que un archivo existe"""
    if os.path.exists(ruta):
        print(f"✓ {descripcion}: OK")
        return True
    else:
        print(f"✗ {descripcion}: NO ENCONTRADO")
        return False


def verificar_paquete(nombre):
    """Verifica que un paquete de Python está instalado"""
    try:
        __import__(nombre)
        print(f"✓ {nombre}: Instalado")
        return True
    except ImportError:
        print(f"✗ {nombre}: NO INSTALADO")
        return False


def verificar_sqlite():
    """Verifica que la base de datos SQLite existe (o se puede crear)."""
    try:
        from db.init_db import ensure_db
        ruta = ensure_db()  # no la sobreescribe si ya existe
        print(f"✓ Base de datos SQLite: OK ({ruta})")
        return True
    except Exception as e:
        print(f"✗ Base de datos SQLite: ERROR - {e}")
        return False


def verificar_modelo_mdl():
    """Verifica que el archivo .mdl vendorizado está accesible."""
    try:
        from src.Controllers.controller import _MDL_PATH_DEFECTO
        from decouple import config, UndefinedValueError
        try:
            ruta = config('MDL_PATH', default=_MDL_PATH_DEFECTO)
        except UndefinedValueError:
            ruta = _MDL_PATH_DEFECTO
        if os.path.isfile(ruta):
            print(f"✓ Archivo del modelo Vensim (.mdl): OK ({ruta})")
            return True
        print(f"✗ Archivo del modelo Vensim (.mdl): NO ENCONTRADO en {ruta}")
        return False
    except Exception as e:
        print(f"✗ Archivo del modelo Vensim (.mdl): ERROR - {e}")
        return False


def main():
    print("=" * 60)
    print("VERIFICACIÓN DE INSTALACIÓN")
    print("Sistema de Gestión de Residuos Sólidos - San Juan de Lurigancho")
    print("=" * 60)
    print()

    errores = 0

    # 1. Verificar archivos del proyecto
    print("1. ARCHIVOS DEL PROYECTO")
    print("-" * 40)
    archivos = [
        ('app.py', 'Archivo principal'),
        ('src/Routes/route.py', 'Rutas'),
        ('src/Controllers/controller.py', 'Controlador'),
        ('src/Models/model.py', 'Modelo'),
        ('src/Connection/connection.py', 'Conexión'),
        ('db/schema.sql', 'Esquema SQLite'),
        ('db/init_db.py', 'Script de inicialización de BD'),
        ('model/residuos_sjl.mdl', 'Modelo Vensim vendorizado'),
        ('templates/landing.html', 'Página de inicio'),
        ('templates/template.html', 'Plantilla de subsistemas'),
        ('templates/error.html', 'Página de error'),
        ('static/css/style.css', 'Estilos CSS'),
    ]

    for archivo, desc in archivos:
        if not verificar_archivo(archivo, desc):
            errores += 1

    print()

    # 2. Verificar paquetes de Python
    print("2. DEPENDENCIAS DE PYTHON")
    print("-" * 40)
    paquetes = ['flask', 'gunicorn', 'pysd', 'decouple', 'numpy']

    for paquete in paquetes:
        if not verificar_paquete(paquete):
            errores += 1

    print()

    # 3. Verificar base de datos SQLite
    print("3. BASE DE DATOS SQLITE")
    print("-" * 40)
    if not verificar_sqlite():
        errores += 1

    print()

    # 4. Verificar archivo .mdl
    print("4. MODELO VENSIM (.MDL)")
    print("-" * 40)
    if not verificar_modelo_mdl():
        errores += 1

    print()
    print("=" * 60)

    if errores == 0:
        print("✓ VERIFICACIÓN COMPLETA: TODO OK")
        print("Puedes ejecutar la aplicación con: python app.py")
    else:
        print(f"✗ VERIFICACIÓN COMPLETA: {errores} ERROR(ES) ENCONTRADO(S)")
        print("Por favor, revisa los errores antes de ejecutar la aplicación.")

    print("=" * 60)


if __name__ == '__main__':
    main()
