from src.Connection.connection import connect, connection_select, connection_execute

TABLAS = {
    'generacion':     'generacion_config',
    'recoleccion':    'recoleccion_config',
    'disposicion':    'disposicion_config',
    'valorizacion':   'valorizacion_config',
    'financiamiento': 'financiamiento_config',
}

# ---------------------------------------------------------------------------
# Configuracion de graficas (niveles a mostrar por subsistema)
# ---------------------------------------------------------------------------
def getModelBySubsistema(subsistema):
    """
    Consulta la configuracion de graficas de un subsistema.
    Retorna lista de diccionarios (nivel, titulo, grupo, unidad, color, ...)
    o un diccionario {'error': ...}.
    """
    tabla = TABLAS.get(subsistema)
    if not tabla:
        return {'error': f'Subsistema desconocido: {subsistema}'}

    conn = connect()
    if isinstance(conn, dict) and 'error' in conn:
        return conn
    try:
        cursor = conn.cursor(dictionary=True)
        query = (f"SELECT nivel, titulo, grupo, eje_x, eje_y, unidad, color, posicion "
                 f"FROM {tabla} ORDER BY posicion ASC")
        # connection_select ya ejecuta y hace fetchall(); no volver a llamar
        # cursor.fetchall() despues (el cursor queda agotado y devuelve []).
        resultado = connection_select(cursor, query)
        cursor.close()
        conn.close()
        return resultado
    except Exception:
        if conn:
            conn.close()
        return {'error': 'Error al consultar la configuracion en la base de datos.'}

def getModelGeneracion():     return getModelBySubsistema('generacion')
def getModelRecoleccion():    return getModelBySubsistema('recoleccion')
def getModelDisposicion():    return getModelBySubsistema('disposicion')
def getModelValorizacion():   return getModelBySubsistema('valorizacion')
def getModelFinanciamiento(): return getModelBySubsistema('financiamiento')

def getConfigCompleta():
    """
    Devuelve un diccionario nivel -> metadatos (titulo, unidad, color, subsistema)
    combinando las 5 tablas de configuracion. Util para el controlador.
    """
    conn = connect()
    if isinstance(conn, dict) and 'error' in conn:
        return conn
    try:
        cursor = conn.cursor(dictionary=True)
        meta = {}
        for subsistema, tabla in TABLAS.items():
            filas = connection_select(cursor,
                f"SELECT nivel, titulo, grupo, unidad, color FROM {tabla} ORDER BY posicion ASC")
            for fila in filas:
                meta[fila['nivel']] = {
                    'titulo': fila['titulo'],
                    'grupo': fila['grupo'],
                    'unidad': fila['unidad'],
                    'color': fila['color'],
                    'subsistema': subsistema,
                }
        cursor.close()
        conn.close()
        return meta
    except Exception:
        if conn:
            conn.close()
        return {'error': 'Error al consultar la configuracion en la base de datos.'}

# ---------------------------------------------------------------------------
# Datos reales (observados)
# ---------------------------------------------------------------------------
def getDatosReales(subsistema=None, niveles=None):
    """
    Devuelve datos reales observados. Puede filtrarse por subsistema y/o
    por una lista de niveles. Retorna lista de dicts {nivel, anio, valor, fuente}.
    """
    conn = connect()
    if isinstance(conn, dict) and 'error' in conn:
        return conn
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT nivel, anio, valor, fuente FROM datos_reales"
        cond, params = [], []
        if subsistema:
            cond.append("subsistema = %s"); params.append(subsistema)
        if niveles:
            marcadores = ",".join(["%s"] * len(niveles))
            cond.append(f"nivel IN ({marcadores})"); params.extend(niveles)
        if cond:
            query += " WHERE " + " AND ".join(cond)
        query += " ORDER BY nivel, anio ASC"
        resultado = connection_select(cursor, query, tuple(params))
        cursor.close()
        conn.close()
        return resultado
    except Exception:
        if conn:
            conn.close()
        return {'error': 'Error al consultar los datos reales en la base de datos.'}

# ---------------------------------------------------------------------------
# Escenarios simulados guardados
# ---------------------------------------------------------------------------
def guardarSimulacion(nombre, descripcion, datos, parametros=None):
    """
    Persiste un escenario simulado. `datos` es una lista de tuplas
    (nivel, anio, valor); `parametros` es un JSON string con las palancas
    aplicadas (o None si es la corrida base). Retorna {'id': ...} o {'error': ...}.
    """
    if not nombre or not datos:
        return {'error': 'Falta el nombre del escenario o los datos a guardar.'}
    conn = connect()
    if isinstance(conn, dict) and 'error' in conn:
        return conn
    try:
        cursor = conn.cursor()
        connection_execute(cursor,
            "INSERT INTO simulaciones (nombre, descripcion, parametros) VALUES (%s, %s, %s)",
            (nombre, descripcion or '', parametros))
        sim_id = cursor.lastrowid
        cursor.executemany(
            "INSERT INTO simulacion_datos (simulacion_id, nivel, anio, valor) VALUES (?, ?, ?, ?)",
            [(sim_id, n, int(a), float(v)) for (n, a, v) in datos])
        conn.commit()
        cursor.close()
        conn.close()
        return {'id': sim_id}
    except Exception:
        if conn:
            conn.close()
        return {'error': 'No se pudo guardar el escenario en la base de datos.'}

def listarSimulaciones():
    """Lista los escenarios guardados (metadatos, sin los datos)."""
    conn = connect()
    if isinstance(conn, dict) and 'error' in conn:
        return conn
    try:
        cursor = conn.cursor(dictionary=True)
        resultado = connection_select(cursor,
            "SELECT id, nombre, descripcion, parametros, creado FROM simulaciones ORDER BY creado DESC")
        for r in resultado:
            if r.get('creado') is not None:
                r['creado'] = str(r['creado'])
        cursor.close()
        conn.close()
        return resultado
    except Exception:
        if conn:
            conn.close()
        return {'error': 'Error al listar los escenarios guardados.'}

def eliminarSimulacion(sim_id):
    """Elimina un escenario guardado (sus datos caen en cascada)."""
    conn = connect()
    if isinstance(conn, dict) and 'error' in conn:
        return conn
    try:
        cursor = conn.cursor()
        connection_execute(cursor, "DELETE FROM simulaciones WHERE id = %s", (sim_id,))
        conn.commit()
        borrado = cursor.rowcount > 0
        cursor.close()
        conn.close()
        if not borrado:
            return {'error': f'No existe el escenario {sim_id}.'}
        return {'ok': True}
    except Exception:
        if conn:
            conn.close()
        return {'error': 'No se pudo eliminar el escenario.'}

def getSimulacion(sim_id):
    """Devuelve los datos de un escenario guardado {nivel, anio, valor}."""
    conn = connect()
    if isinstance(conn, dict) and 'error' in conn:
        return conn
    try:
        cursor = conn.cursor(dictionary=True)
        resultado = connection_select(cursor,
            "SELECT nivel, anio, valor FROM simulacion_datos WHERE simulacion_id = %s ORDER BY nivel, anio",
            (sim_id,))
        cursor.close()
        conn.close()
        return resultado
    except Exception:
        if conn:
            conn.close()
        return {'error': 'Error al leer el escenario guardado.'}
