import os
import hashlib
import urllib3
import pysd
from decouple import config

from src.Models.model import (
    getModelBySubsistema, getConfigCompleta, getDatosReales,
    guardarSimulacion, listarSimulaciones, getSimulacion, eliminarSimulacion,
)

# Caché en memoria de simulaciones (la corrida de PySD es costosa).
# Clave: (hash del .mdl, parámetros ordenados). Se conservan las últimas corridas.
_CACHE = {'hash': None, 'runs': {}}
_CACHE_MAX = 8

# Palancas de política ajustables desde el panel (lista blanca con rangos).
# Solo estas constantes del modelo pueden modificarse vía API.
PALANCAS = [
    {'nombre': 'voluntad politica',       'etiqueta': 'Voluntad política de reciclaje',
     'min': 0.0,    'max': 1.0,      'paso': 0.05,   'defecto': 0.5,    'unidad': '0–1',        'subsistema': 'Valorización'},
    {'nombre': 'arbitrio por habitante',  'etiqueta': 'Arbitrio por habitante',
     'min': 60,     'max': 240,      'paso': 5,      'defecto': 120,    'unidad': 'S//hab/año', 'subsistema': 'Financiamiento'},
    {'nombre': 'transferencias MEF',      'etiqueta': 'Transferencias del MEF',
     'min': 0,      'max': 60000000, 'paso': 1000000,'defecto': 18000000,'unidad': 'S//año',    'subsistema': 'Financiamiento'},
    {'nombre': 'Obj cobertura',           'etiqueta': 'Meta de cobertura de recolección',
     'min': 0.5,    'max': 1.0,      'paso': 0.05,   'defecto': 0.9,    'unidad': '0–1',        'subsistema': 'Recolección'},
    {'nombre': 'fracc presupuesto flota', 'etiqueta': 'Presupuesto destinado a flota',
     'min': 0.05,   'max': 0.40,     'paso': 0.01,   'defecto': 0.18,   'unidad': 'fracción',   'subsistema': 'Recolección'},
    {'nombre': 'tasa natalidad',          'etiqueta': 'Tasa de natalidad',
     'min': 0.010,  'max': 0.025,    'paso': 0.001,  'defecto': 0.018,  'unidad': '1/año',      'subsistema': 'Generación'},
]
_PALANCAS_IDX = {p['nombre']: p for p in PALANCAS}


def validar_params(params):
    """
    Filtra y valida parámetros contra la lista blanca de palancas.
    Retorna dict limpio (solo valores distintos al defecto) o {'error': ...}.
    """
    if not params:
        return {}
    limpio = {}
    for nombre, valor in params.items():
        p = _PALANCAS_IDX.get(nombre)
        if p is None:
            return {'error': f'Parámetro no permitido: "{nombre}".'}
        try:
            v = float(valor)
        except (TypeError, ValueError):
            return {'error': f'Valor no numérico para "{nombre}".'}
        if not (p['min'] <= v <= p['max']):
            return {'error': f'"{nombre}" fuera de rango [{p["min"]}, {p["max"]}].'}
        if v != p['defecto']:
            limpio[nombre] = v
    return limpio


# ---------------------------------------------------------------------------
# Simulación del modelo Vensim con PySD
# ---------------------------------------------------------------------------
def _descargar_mdl():
    """Descarga el .mdl desde XAMPP y lo guarda en ./temp. Retorna la ruta o {'error'}."""
    try:
        mdl_url = config('MDL_URL')
        mdl_filename = config('MDL_FILENAME')
    except Exception:
        return {'error': 'Variables MDL_URL / MDL_FILENAME no configuradas en el archivo .env.'}

    try:
        http = urllib3.PoolManager(retries=urllib3.Retry(2), timeout=10.0)
        resp = http.request('GET', mdl_url)
        if resp.status != 200:
            return {'error': 'No se pudo descargar el modelo. Verifica que XAMPP (Apache) esté corriendo.'}
        temp_dir = './temp'
        os.makedirs(temp_dir, exist_ok=True)
        ruta = os.path.join(temp_dir, mdl_filename)
        with open(ruta, 'wb') as f:
            f.write(resp.data)
        return {'ruta': ruta, 'hash': hashlib.md5(resp.data).hexdigest()}
    except Exception:
        return {'error': 'No se pudo descargar el modelo. Verifica que XAMPP (Apache) esté corriendo.'}


def simular(params=None, forzar=False):
    """
    Corre la simulación (con caché por escenario de parámetros).
    Retorna {'years': [...], 'data': {nivel: [valores]}} o {'error': ...}.
    `params` es un dict ya validado de palancas {nombre: valor}.
    """
    descarga = _descargar_mdl()
    if 'error' in descarga:
        return descarga

    if _CACHE['hash'] != descarga['hash']:
        _CACHE['hash'] = descarga['hash']
        _CACHE['runs'] = {}

    clave = tuple(sorted((params or {}).items()))
    if not forzar and clave in _CACHE['runs']:
        return _CACHE['runs'][clave]

    try:
        modelo = pysd.read_vensim(descarga['ruta'])
        df = modelo.run(params=dict(params)) if params else modelo.run()
    except Exception:
        return {'error': 'Error al simular el modelo Vensim con PySD.'}

    years = [int(round(y)) for y in df.index.tolist()]
    data = {col: [None if v != v else float(v) for v in df[col].tolist()] for col in df.columns}

    resultado = {'years': years, 'data': data}
    if len(_CACHE['runs']) >= _CACHE_MAX:
        _CACHE['runs'].pop(next(iter(_CACHE['runs'])))
    _CACHE['runs'][clave] = resultado
    return resultado


# ---------------------------------------------------------------------------
# Series simuladas (con metadatos de la BD para color / unidad / título)
# ---------------------------------------------------------------------------
def get_series(niveles, params=None):
    """
    Devuelve las series simuladas de los niveles pedidos, con metadatos.
    { 'years': [...], 'series': { nivel: {titulo, unidad, color, grupo, valores:[...]} } }
    """
    sim = simular(params=params)
    if 'error' in sim:
        return sim
    meta = getConfigCompleta()
    if isinstance(meta, dict) and 'error' in meta:
        return meta

    series = {}
    for nivel in niveles:
        if nivel not in sim['data']:
            return {'error': f'El nivel "{nivel}" no existe en el modelo Vensim.'}
        m = meta.get(nivel, {})
        series[nivel] = {
            'titulo': m.get('titulo', nivel),
            'unidad': m.get('unidad', ''),
            'color': m.get('color', '#2F7A6E'),
            'grupo': m.get('grupo', ''),
            'valores': sim['data'][nivel],
        }
    return {'years': sim['years'], 'series': series}


# ---------------------------------------------------------------------------
# Comparación real vs simulado + ratio de diferencia
# ---------------------------------------------------------------------------
def _mape(reales, simulados):
    """Error porcentual absoluto medio (%) sobre los años con dato real != 0."""
    errores = []
    for r, s in zip(reales, simulados):
        if r is not None and s is not None and r != 0:
            errores.append(abs(r - s) / abs(r))
    if not errores:
        return None
    return round(100 * sum(errores) / len(errores), 2)


def comparar(subsistema, niveles, params=None):
    """
    Para cada nivel: serie simulada (todo el horizonte), serie real (años observados),
    diferencia (real - sim), ratio (real / sim) y MAPE. Solo los años con dato real
    tienen real/diferencia/ratio; el resto queda en None.
    """
    sim = get_series(niveles, params=params)
    if 'error' in sim:
        return sim
    reales = getDatosReales(subsistema=subsistema, niveles=niveles)
    if isinstance(reales, dict) and 'error' in reales:
        return reales

    # Mapa nivel -> {anio: valor real}
    real_map = {}
    for fila in reales:
        real_map.setdefault(fila['nivel'], {})[int(fila['anio'])] = float(fila['valor'])

    years = sim['years']
    salida = {'years': years, 'series': {}}
    for nivel, info in sim['series'].items():
        rm = real_map.get(nivel, {})
        serie_real, dif, ratio = [], [], []
        for i, y in enumerate(years):
            s = info['valores'][i]
            r = rm.get(y)
            serie_real.append(r)
            if r is not None and s is not None:
                dif.append(round(r - s, 4))
                ratio.append(round(r / s, 4) if s != 0 else None)
            else:
                dif.append(None)
                ratio.append(None)
        salida['series'][nivel] = {
            'titulo': info['titulo'],
            'unidad': info['unidad'],
            'color': info['color'],
            'grupo': info['grupo'],
            'simulado': info['valores'],
            'real': serie_real,
            'diferencia': dif,
            'ratio': ratio,
            'mape': _mape(serie_real, info['valores']),
            'fuente': next((f['fuente'] for f in reales if f['nivel'] == nivel), None),
        }
    return salida


def ratio_entre(nivel_a, nivel_b, params=None):
    """Serie del cociente nivel_a / nivel_b a lo largo del horizonte."""
    res = get_series([nivel_a, nivel_b], params=params)
    if 'error' in res:
        return res
    years = res['years']
    a = res['series'][nivel_a]['valores']
    b = res['series'][nivel_b]['valores']
    valores = []
    for va, vb in zip(a, b):
        valores.append(round(va / vb, 6) if (va is not None and vb not in (None, 0)) else None)
    return {
        'years': years,
        'valores': valores,
        'etiqueta': f"{res['series'][nivel_a]['titulo']} / {res['series'][nivel_b]['titulo']}",
        'unidad_a': res['series'][nivel_a]['unidad'],
        'unidad_b': res['series'][nivel_b]['unidad'],
    }


# ---------------------------------------------------------------------------
# Guardar / listar escenarios simulados
# ---------------------------------------------------------------------------
def guardar_escenario(nombre, descripcion, niveles, params=None):
    """Guarda en la BD la serie simulada (con las palancas aplicadas) de los niveles indicados."""
    import json
    sim = get_series(niveles, params=params)
    if 'error' in sim:
        return sim
    datos = []
    for nivel, info in sim['series'].items():
        for y, v in zip(sim['years'], info['valores']):
            if v is not None:
                datos.append((nivel, y, v))
    parametros_json = json.dumps(params, ensure_ascii=False) if params else None
    return guardarSimulacion(nombre, descripcion, datos, parametros_json)


def listar_escenarios():
    return listarSimulaciones()


def eliminar_escenario(sim_id):
    return eliminarSimulacion(sim_id)


def get_escenario(sim_id):
    filas = getSimulacion(sim_id)
    if isinstance(filas, dict) and 'error' in filas:
        return filas
    years = sorted({int(f['anio']) for f in filas})
    series = {}
    for f in filas:
        series.setdefault(f['nivel'], {})[int(f['anio'])] = float(f['valor'])
    out = {'years': years, 'series': {}}
    for nivel, vals in series.items():
        out['series'][nivel] = [vals.get(y) for y in years]
    return out
