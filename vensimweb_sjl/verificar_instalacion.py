"""
Script de verificación de instalación
Ejecuta este script antes de iniciar la aplicación para verificar que todo está configurado correctamente.
"""

import sys
import os
from pathlib import Path

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

def verificar_env():
    """Verifica las variables de entorno"""
    try:
        from decouple import config
        variables = ['DB_HOST', 'DB_PORT', 'DB_USER', 'DB_NAME', 'MDL_URL', 'MDL_FILENAME']
        todas_ok = True

        for var in variables:
            try:
                valor = config(var)
                print(f"✓ {var}: Configurado")
            except:
                print(f"✗ {var}: NO CONFIGURADO en .env")
                todas_ok = False

        # NGROK_TOKEN es opcional
        try:
            token = config('NGROK_TOKEN')
            if token == 'TU_TOKEN_AQUI':
                print(f"⚠ NGROK_TOKEN: No configurado (opcional - solo para acceso público)")
            else:
                print(f"✓ NGROK_TOKEN: Configurado")
        except:
            print(f"⚠ NGROK_TOKEN: No configurado (opcional)")

        return todas_ok
    except Exception as e:
        print(f"✗ Error al leer .env: {e}")
        return False

def verificar_mysql():
    """Verifica la conexión a MySQL"""
    try:
        import mysql.connector
        from decouple import config

        conn = mysql.connector.connect(
            host=config('DB_HOST'),
            port=config('DB_PORT'),
            user=config('DB_USER'),
            password=config('DB_PASSWORD', default=''),
            database=config('DB_NAME')
        )
        conn.close()
        print(f"✓ Conexión a MySQL: OK")
        return True
    except Exception as e:
        print(f"✗ Conexión a MySQL: ERROR - {e}")
        return False

def verificar_xampp():
    """Verifica que el archivo .mdl está accesible"""
    try:
        import urllib3
        from decouple import config

        http = urllib3.PoolManager()
        url = config('MDL_URL')
        response = http.request('GET', url, timeout=5.0)

        if response.status == 200:
            print(f"✓ Archivo .mdl en XAMPP: ACCESIBLE")
            return True
        else:
            print(f"✗ Archivo .mdl en XAMPP: NO ACCESIBLE (código {response.status})")
            return False
    except Exception as e:
        print(f"✗ Archivo .mdl en XAMPP: ERROR - {e}")
        return False

def main():
    print("="*60)
    print("VERIFICACIÓN DE INSTALACIÓN")
    print("Sistema de Gestión de Residuos Sólidos - San Juan de Lurigancho")
    print("="*60)
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
        ('.env', 'Variables de entorno'),
        ('backup/vensimweb_sjl.sql', 'Script SQL'),
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
    paquetes = ['flask', 'pyngrok', 'pysd', 'mysql.connector', 'decouple',
                'numpy', 'urllib3', 'mpld3', 'matplotlib']

    for paquete in paquetes:
        nombre_import = 'mysql.connector' if paquete == 'mysql.connector' else paquete
        if paquete == 'decouple':
            nombre_import = 'decouple'
        if paquete == 'mysql.connector':
            nombre_import = 'mysql.connector'

        if not verificar_paquete(nombre_import):
            errores += 1

    print()

    # 3. Verificar variables de entorno
    print("3. VARIABLES DE ENTORNO")
    print("-" * 40)
    if not verificar_env():
        errores += 1

    print()

    # 4. Verificar MySQL
    print("4. BASE DE DATOS MYSQL")
    print("-" * 40)
    if not verificar_mysql():
        errores += 1

    print()

    # 5. Verificar XAMPP y archivo .mdl
    print("5. XAMPP Y ARCHIVO .MDL")
    print("-" * 40)
    if not verificar_xampp():
        errores += 1

    print()
    print("="*60)

    if errores == 0:
        print("✓ VERIFICACIÓN COMPLETA: TODO OK")
        print("Puedes ejecutar la aplicación con: python app.py")
    else:
        print(f"✗ VERIFICACIÓN COMPLETA: {errores} ERROR(ES) ENCONTRADO(S)")
        print("Por favor, revisa los errores antes de ejecutar la aplicación.")

    print("="*60)

if __name__ == '__main__':
    main()
