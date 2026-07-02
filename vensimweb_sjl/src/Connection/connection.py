import mysql.connector
from decouple import config

def connect():
    """
    Establece conexión con MySQL usando variables de entorno.
    Retorna objeto conexión si tiene éxito, o diccionario con error.
    """
    try:
        connection = mysql.connector.connect(
            host=config('DB_HOST'),
            port=config('DB_PORT'),
            user=config('DB_USER'),
            password=config('DB_PASSWORD'),
            database=config('DB_NAME')
        )
        return connection
    except mysql.connector.Error as err:
        return {'error': 'No se pudo conectar a MySQL'}
    except Exception as e:
        return {'error': f'Variable de entorno no configurada. Revisa el archivo .env'}

def connection_select(cursorObject, select_stmt):
    """
    Ejecuta una consulta SELECT y retorna los resultados.
    """
    cursorObject.execute(select_stmt)
    return cursorObject.fetchall()
