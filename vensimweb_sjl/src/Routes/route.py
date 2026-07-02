from flask import Blueprint, render_template
from src.Controllers.controller import controller

routes = Blueprint('routes', __name__)

# Definir las pestañas de navegación (se usan en todas las vistas)
PESTANAS = [
    {'nombre': 'Generación', 'ruta': '/generacion'},
    {'nombre': 'Recolección', 'ruta': '/recoleccion'},
    {'nombre': 'Disposición', 'ruta': '/disposicion'},
    {'nombre': 'Valorización', 'ruta': '/valorizacion'},
    {'nombre': 'Financiamiento', 'ruta': '/financiamiento'}
]

# Indicadores principales por subsistema
INDICADORES = {
    'generacion': 'Generación per cápita (GPC) — kg/hab/día',
    'recoleccion': 'Cobertura de recolección — %',
    'disposicion': 'Vida útil remanente de rellenos — años',
    'valorizacion': 'Tasa de reciclaje formal — %',
    'financiamiento': 'Presupuesto per cápita — S/hab/año'
}

# Nombres legibles de subsistemas
NOMBRES_SUBSISTEMAS = {
    'generacion': 'Generación',
    'recoleccion': 'Recolección',
    'disposicion': 'Disposición',
    'valorizacion': 'Valorización',
    'financiamiento': 'Financiamiento'
}

@routes.route('/')
def landing():
    """Renderiza la landing page"""
    return render_template('landing.html')

@routes.route('/generacion')
def generacion():
    """Vista del subsistema Generación"""
    resultado = controller('generacion')

    if isinstance(resultado, dict) and 'error' in resultado:
        return render_template('error.html',
                             mensaje=resultado['error'],
                             pestanas=PESTANAS)

    return render_template('template.html',
                         niveles=resultado,
                         subsistema=NOMBRES_SUBSISTEMAS['generacion'],
                         indicador=INDICADORES['generacion'],
                         pestanas=PESTANAS,
                         ruta_activa='/generacion')

@routes.route('/recoleccion')
def recoleccion():
    """Vista del subsistema Recolección"""
    resultado = controller('recoleccion')

    if isinstance(resultado, dict) and 'error' in resultado:
        return render_template('error.html',
                             mensaje=resultado['error'],
                             pestanas=PESTANAS)

    return render_template('template.html',
                         niveles=resultado,
                         subsistema=NOMBRES_SUBSISTEMAS['recoleccion'],
                         indicador=INDICADORES['recoleccion'],
                         pestanas=PESTANAS,
                         ruta_activa='/recoleccion')

@routes.route('/disposicion')
def disposicion():
    """Vista del subsistema Disposición"""
    resultado = controller('disposicion')

    if isinstance(resultado, dict) and 'error' in resultado:
        return render_template('error.html',
                             mensaje=resultado['error'],
                             pestanas=PESTANAS)

    return render_template('template.html',
                         niveles=resultado,
                         subsistema=NOMBRES_SUBSISTEMAS['disposicion'],
                         indicador=INDICADORES['disposicion'],
                         pestanas=PESTANAS,
                         ruta_activa='/disposicion')

@routes.route('/valorizacion')
def valorizacion():
    """Vista del subsistema Valorización"""
    resultado = controller('valorizacion')

    if isinstance(resultado, dict) and 'error' in resultado:
        return render_template('error.html',
                             mensaje=resultado['error'],
                             pestanas=PESTANAS)

    return render_template('template.html',
                         niveles=resultado,
                         subsistema=NOMBRES_SUBSISTEMAS['valorizacion'],
                         indicador=INDICADORES['valorizacion'],
                         pestanas=PESTANAS,
                         ruta_activa='/valorizacion')

@routes.route('/financiamiento')
def financiamiento():
    """Vista del subsistema Financiamiento"""
    resultado = controller('financiamiento')

    if isinstance(resultado, dict) and 'error' in resultado:
        return render_template('error.html',
                             mensaje=resultado['error'],
                             pestanas=PESTANAS)

    return render_template('template.html',
                         niveles=resultado,
                         subsistema=NOMBRES_SUBSISTEMAS['financiamiento'],
                         indicador=INDICADORES['financiamiento'],
                         pestanas=PESTANAS,
                         ruta_activa='/financiamiento')
