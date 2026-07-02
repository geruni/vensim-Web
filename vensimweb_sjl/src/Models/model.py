from src.Connection.connection import connect, connection_select

def getModelBySubsistema(subsistema):
    """
    Función genérica para consultar la configuración de gráficas de cualquier subsistema.
    Retorna lista de diccionarios con la configuración, o diccionario con error.
    """
    tablas = {
        'generacion':     'generacion_config',
        'recoleccion':    'recoleccion_config',
        'disposicion':    'disposicion_config',
        'valorizacion':   'valorizacion_config',
        'financiamiento': 'financiamiento_config',
    }

    tabla = tablas.get(subsistema)
    if not tabla:
        return {'error': f'Subsistema desconocido: {subsistema}'}

    connection = connect()
    if isinstance(connection, dict) and 'error' in connection:
        return connection

    try:
        cursor = connection.cursor(dictionary=True)
        query = f"SELECT id, nivel, titulo, eje_x, eje_y, color, posicion FROM {tabla} ORDER BY posicion ASC"
        connection_select(cursor, query)
        resultado = cursor.fetchall()
        cursor.close()
        connection.close()
        return resultado
    except Exception as e:
        if connection:
            connection.close()
        return {'error': 'Error al consultar la base de datos'}

def getModelGeneracion():
    """Consulta configuración del subsistema Generación"""
    return getModelBySubsistema('generacion')

def getModelRecoleccion():
    """Consulta configuración del subsistema Recolección"""
    return getModelBySubsistema('recoleccion')

def getModelDisposicion():
    """Consulta configuración del subsistema Disposición"""
    return getModelBySubsistema('disposicion')

def getModelValorizacion():
    """Consulta configuración del subsistema Valorización"""
    return getModelBySubsistema('valorizacion')

def getModelFinanciamiento():
    """Consulta configuración del subsistema Financiamiento"""
    return getModelBySubsistema('financiamiento')
