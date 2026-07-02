import os
import urllib3
import pysd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mpld3
from decouple import config
from src.Models.model import getModelBySubsistema

def controller(subsistema):
    """
    Controlador principal que procesa un subsistema:
    1. Descarga el archivo .mdl desde XAMPP
    2. Lo simula con pysd
    3. Consulta la configuración de gráficas desde MySQL
    4. Genera gráficas interactivas con matplotlib + mpld3
    5. Retorna diccionario con las gráficas HTML o error
    """

    # 1. Leer variables de entorno
    try:
        mdl_url = config('MDL_URL')
        mdl_filename = config('MDL_FILENAME')
    except Exception as e:
        return {'error': f'Variable de entorno no configurada. Revisa el archivo .env'}

    # 2. Descargar el archivo .mdl desde XAMPP
    try:
        http = urllib3.PoolManager()
        response = http.request('GET', mdl_url)

        if response.status != 200:
            return {'error': 'No se pudo descargar el modelo. Verifica que XAMPP esté corriendo.'}

        # Crear carpeta temporal si no existe
        temp_dir = './temp'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Guardar archivo localmente
        local_mdl_path = os.path.join(temp_dir, mdl_filename)
        with open(local_mdl_path, 'wb') as f:
            f.write(response.data)

    except Exception as e:
        return {'error': 'No se pudo descargar el modelo. Verifica que XAMPP esté corriendo.'}

    # 3. Leer y simular el modelo con pysd
    try:
        modelo = pysd.read_vensim(local_mdl_path)
        resultado_sim = modelo.run()
    except Exception as e:
        return {'error': 'Error al simular el modelo Vensim'}

    # 4. Consultar la tabla MySQL del subsistema
    datos_bd = getModelBySubsistema(subsistema)
    if isinstance(datos_bd, dict) and 'error' in datos_bd:
        return datos_bd

    # 5. Generar gráficas para cada nivel configurado
    niveles = {}

    for fila in datos_bd:
        nivel_nombre = fila['nivel']
        titulo = fila['titulo']
        eje_x = fila['eje_x']
        eje_y = fila['eje_y']
        color = fila['color']
        posicion = fila['posicion']

        # Verificar que el nivel existe en el resultado de la simulación
        if nivel_nombre not in resultado_sim.columns:
            tabla_nombre = f"{subsistema}_config"
            return {'error': f'El nivel "{nivel_nombre}" no existe en el modelo Vensim. Revisa la tabla {tabla_nombre}.'}

        # Crear figura matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))

        # Extraer datos de la simulación
        x_data = resultado_sim.index
        y_data = resultado_sim[nivel_nombre]

        # Graficar
        ax.plot(x_data, y_data, color=color, linewidth=2)
        ax.set_xlabel(eje_x, fontsize=12)
        ax.set_ylabel(eje_y, fontsize=12)
        ax.set_title(titulo, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Convertir a HTML interactivo con mpld3
        html_grafica = mpld3.fig_to_html(fig)
        plt.close(fig)

        # Guardar en diccionario
        niveles[posicion] = {
            'titulo': titulo,
            'grafica': html_grafica
        }

    # 6. Retornar diccionario ordenado por posición
    return dict(sorted(niveles.items()))
