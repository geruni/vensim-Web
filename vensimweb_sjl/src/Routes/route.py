import json
from flask import Blueprint, render_template, request, jsonify, Response
from src.Models.model import getModelBySubsistema, getConfigCompleta
from src.Controllers.controller import (
    get_series, comparar, ratio_entre,
    guardar_escenario, listar_escenarios, get_escenario, eliminar_escenario,
    PALANCAS, validar_params,
)

routes = Blueprint('routes', __name__)

PESTANAS = [
    {'clave': 'generacion',     'nombre': 'Generación',     'ruta': '/dashboard/generacion',     'icono': '♻️'},
    {'clave': 'recoleccion',    'nombre': 'Recolección',    'ruta': '/dashboard/recoleccion',    'icono': '🚛'},
    {'clave': 'disposicion',    'nombre': 'Disposición',    'ruta': '/dashboard/disposicion',    'icono': '🏗️'},
    {'clave': 'valorizacion',   'nombre': 'Valorización',   'ruta': '/dashboard/valorizacion',   'icono': '📦'},
    {'clave': 'financiamiento', 'nombre': 'Financiamiento', 'ruta': '/dashboard/financiamiento', 'icono': '💰'},
]

INDICADORES = {
    'generacion':     'Generación per cápita (GPC) — kg/hab/día',
    'recoleccion':    'Cobertura de recolección — %',
    'disposicion':    'Vida útil remanente de rellenos — años',
    'valorizacion':   'Tasa de reciclaje formal — %',
    'financiamiento': 'Presupuesto per cápita — S/hab/año',
}

NOMBRES = {p['clave']: p['nombre'] for p in PESTANAS}


def _niveles_param():
    """Lee ?niveles=a,b,c y devuelve la lista (o vacía)."""
    raw = request.args.get('niveles', '').strip()
    return [n for n in raw.split(',') if n] if raw else []


def _params_param(fuente=None):
    """
    Lee las palancas what-if desde ?params=<json> (o de un dict ya deserializado)
    y las valida contra la lista blanca. Retorna dict limpio o {'error': ...}.
    """
    if fuente is None:
        raw = request.args.get('params', '').strip()
        if not raw:
            return {}
        try:
            fuente = json.loads(raw)
        except ValueError:
            return {'error': 'El parámetro "params" no es JSON válido.'}
    if not isinstance(fuente, dict):
        return {'error': 'Las palancas deben enviarse como objeto JSON.'}
    return validar_params(fuente)


def _json_or_error(payload, code_ok=200):
    if isinstance(payload, dict) and 'error' in payload:
        return jsonify(payload), 502
    return jsonify(payload), code_ok


# ---------------------------------------------------------------------------
# Vistas
# ---------------------------------------------------------------------------
@routes.route('/favicon.ico')
def favicon():
    return Response(status=204)


@routes.route('/')
def landing():
    return render_template('landing.html', pestanas=PESTANAS, indicadores=INDICADORES)


@routes.route('/dashboard')
@routes.route('/dashboard/<subsistema>')
def dashboard(subsistema='generacion'):
    if subsistema not in NOMBRES:
        subsistema = 'generacion'

    config_sub = getModelBySubsistema(subsistema)
    if isinstance(config_sub, dict) and 'error' in config_sub:
        return render_template('error.html', mensaje=config_sub['error'], pestanas=PESTANAS)

    todos = getConfigCompleta()
    if isinstance(todos, dict) and 'error' in todos:
        return render_template('error.html', mensaje=todos['error'], pestanas=PESTANAS)

    # Lista plana para el selector de ratios y la comparación de escenarios
    catalogo = [{'nivel': n, 'titulo': m['titulo'], 'subsistema': m['subsistema'],
                 'unidad': m['unidad'], 'color': m['color']}
                for n, m in todos.items()]

    return render_template(
        'dashboard.html',
        pestanas=PESTANAS,
        subsistema=subsistema,
        subsistema_nombre=NOMBRES[subsistema],
        indicador=INDICADORES[subsistema],
        niveles=config_sub,
        catalogo=catalogo,
    )


# ---------------------------------------------------------------------------
# API JSON
# ---------------------------------------------------------------------------
@routes.route('/api/palancas')
def api_palancas():
    """Lista blanca de palancas what-if con sus rangos, para construir los sliders."""
    return jsonify(PALANCAS)


@routes.route('/api/series')
def api_series():
    niveles = _niveles_param()
    if not niveles:
        return jsonify({'error': 'No se indicaron niveles.'}), 400
    params = _params_param()
    if 'error' in params:
        return jsonify(params), 400
    return _json_or_error(get_series(niveles, params=params))


@routes.route('/api/comparar')
def api_comparar():
    subsistema = request.args.get('subsistema', '')
    niveles = _niveles_param()
    if not subsistema or not niveles:
        return jsonify({'error': 'Faltan parámetros subsistema/niveles.'}), 400
    params = _params_param()
    if 'error' in params:
        return jsonify(params), 400
    return _json_or_error(comparar(subsistema, niveles, params=params))


@routes.route('/api/ratio')
def api_ratio():
    a = request.args.get('a', '')
    b = request.args.get('b', '')
    if not a or not b:
        return jsonify({'error': 'Faltan las variables a/b para el ratio.'}), 400
    params = _params_param()
    if 'error' in params:
        return jsonify(params), 400
    return _json_or_error(ratio_entre(a, b, params=params))


@routes.route('/api/guardar', methods=['POST'])
def api_guardar():
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombre') or '').strip()
    descripcion = (data.get('descripcion') or '').strip()
    niveles = data.get('niveles') or []
    if not nombre or not niveles:
        return jsonify({'error': 'Indica un nombre y al menos un nivel para guardar.'}), 400
    params = _params_param(data.get('params') or {})
    if 'error' in params:
        return jsonify(params), 400
    return _json_or_error(guardar_escenario(nombre, descripcion, niveles, params=params))


@routes.route('/api/escenarios')
def api_escenarios():
    return _json_or_error(listar_escenarios())


@routes.route('/api/escenario/<int:sim_id>')
def api_escenario(sim_id):
    return _json_or_error(get_escenario(sim_id))


@routes.route('/api/escenario/<int:sim_id>', methods=['DELETE'])
def api_escenario_eliminar(sim_id):
    return _json_or_error(eliminar_escenario(sim_id))
