# Instrucciones para Claude Code
## Proyecto: Sistema de Gestión de Residuos Sólidos — San Juan de Lurigancho
## Aplicación web que simula un modelo Vensim y muestra sus resultados en el navegador

---

## CONTEXTO DEL PROYECTO

Este proyecto es una tarea universitaria de **Dinámica de Sistemas** (Universidad Nacional de Ingeniería, Lima, Perú). El objetivo es tomar un modelo de simulación hecho en Vensim (.mdl) y mostrarlo en una página web que cualquier persona pueda abrir desde su celular o laptop, sin instalar nada.

El modelo simula la **gestión de residuos sólidos en San Juan de Lurigancho**, el distrito más poblado de Lima (~1.2 millones de habitantes). El modelo tiene 5 subsistemas: Generación, Recolección, Disposición final, Valorización y Financiamiento.

---

## DECISIONES YA TOMADAS — NO CAMBIAR

Estas decisiones fueron definidas explícitamente. No propongas alternativas:

1. **Un solo archivo `.mdl`** llamado `residuos_sjl.mdl` con todos los subsistemas dentro. No son 5 archivos separados.
2. **Flask** como framework backend (Python).
3. **XAMPP** para servidor local Apache + MySQL. El archivo `.mdl` vive dentro de XAMPP en `C:\xampp\htdocs\assets\vensim\residuos_sjl.mdl`.
4. **ngrok** para exponer la app localmente a internet de forma pública.
5. **PySD** para leer y simular el archivo `.mdl` desde Python.
6. **Matplotlib + mpld3** para generar gráficas interactivas en HTML.
7. **MySQL** para guardar la configuración visual de las gráficas (títulos, colores, ejes, posición). **No guarda resultados de simulación** — solo configuración.
8. **5 tablas MySQL**, una por subsistema (no una tabla única).
9. **Arquitectura MVC + Route**, igual al manual del profesor de referencia.
10. **Landing page** como pantalla de bienvenida antes de las pestañas.
11. **Pestañas** de navegación (una por subsistema), visibles en todas las vistas.
12. **Generación SÍ tiene submodelo** por tipo de residuo: `Generacion_organicos` (50%), `Generacion_reciclables` (30%), `Generacion_no_aprovechables` (20%), que suman `generacion_bruta`. Fuente: caracterización física PIGARS SJL.
13. **La discrepancia de Valorización** usa `brecha_reciclaje = potencial_reciclaje - valorizacion_total`, no un objetivo político del 20%. `potencial_reciclaje = Generacion_reciclables * 365` viene de Vista 02 como shadow variable hacia Vista 05.

---

## ESTRUCTURA DE CARPETAS — EXACTA

Crea exactamente esta estructura. No agregues carpetas extra:

```
vensimweb_sjl/
│
├── .env                          # Variables de entorno
├── requirements.txt              # Dependencias Python
├── app.py                        # Punto de entrada: Flask + ngrok
│
├── src/
│   ├── Routes/
│   │   └── route.py
│   ├── Controllers/
│   │   └── controller.py
│   ├── Models/
│   │   └── model.py
│   └── Connection/
│       └── connection.py
│
├── templates/
│   ├── landing.html
│   ├── template.html
│   └── error.html
│
├── static/
│   └── css/
│       └── style.css
│
└── backup/
    └── vensimweb_sjl.sql
```

Y en XAMPP (fuera del proyecto, no tocar):
```
C:\xampp\htdocs\assets\vensim\
    └── residuos_sjl.mdl          ← UN SOLO ARCHIVO .mdl
```

---

## ARCHIVO .env

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=vensimweb_sjl
NGROK_TOKEN=TU_TOKEN_AQUI
MDL_URL=http://localhost/assets/vensim/residuos_sjl.mdl
MDL_FILENAME=residuos_sjl.mdl
```

---

## ARCHIVO requirements.txt

```
flask
pyngrok
pysd
mysql-connector-python
python-decouple
numpy
urllib3
mpld3
matplotlib
```

---

## BASE DE DATOS — vensimweb_sjl.sql

5 tablas, todas con la misma estructura. Genera datos de ejemplo en cada una con los nombres de niveles reales del modelo.

Los **nombres de nivel exactos** dentro del `.mdl` que se usarán son:

| Tabla | Niveles del modelo (nombre exacto en el .mdl) |
|---|---|
| `generacion_config` | `Poblacion`, `GPC`, `generacion_bruta`, `Generacion_organicos`, `Generacion_reciclables`, `Generacion_no_aprovechables` |
| `recoleccion_config` | `Residuos_dispersos`, `Compactadores`, `Volquetes`, `Barandas`, `Flota_operativa`, `cobertura_recoleccion` |
| `disposicion_config` | `Volumen_relleno_total`, `Volumen_Portillo`, `Volumen_Huaycoloro`, `vida_util_remanente`, `costo_unit_disposicion` |
| `valorizacion_config` | `Recicladores_formalizados`, `valorizacion_total`, `tasa_reciclaje`, `ingreso_reciclaje`, `potencial_reciclaje`, `brecha_reciclaje` |
| `financiamiento_config` | `Presupuesto_disponible`, `Morosidad`, `recaudacion_efectiva`, `deficit_financiero`, `presupuesto_per_capita` |

```sql
CREATE DATABASE IF NOT EXISTS vensimweb_sjl;
USE vensimweb_sjl;

CREATE TABLE generacion_config (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    nivel    VARCHAR(100) NOT NULL,
    titulo   VARCHAR(150),
    eje_x    VARCHAR(100),
    eje_y    VARCHAR(100),
    color    VARCHAR(20),
    posicion INT
);

CREATE TABLE recoleccion_config (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    nivel    VARCHAR(100) NOT NULL,
    titulo   VARCHAR(150),
    eje_x    VARCHAR(100),
    eje_y    VARCHAR(100),
    color    VARCHAR(20),
    posicion INT
);

CREATE TABLE disposicion_config (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    nivel    VARCHAR(100) NOT NULL,
    titulo   VARCHAR(150),
    eje_x    VARCHAR(100),
    eje_y    VARCHAR(100),
    color    VARCHAR(20),
    posicion INT
);

CREATE TABLE valorizacion_config (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    nivel    VARCHAR(100) NOT NULL,
    titulo   VARCHAR(150),
    eje_x    VARCHAR(100),
    eje_y    VARCHAR(100),
    color    VARCHAR(20),
    posicion INT
);

CREATE TABLE financiamiento_config (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    nivel    VARCHAR(100) NOT NULL,
    titulo   VARCHAR(150),
    eje_x    VARCHAR(100),
    eje_y    VARCHAR(100),
    color    VARCHAR(20),
    posicion INT
);

-- Datos de ejemplo
INSERT INTO generacion_config (nivel, titulo, eje_x, eje_y, color, posicion) VALUES
('Poblacion',                   'Población de SJL',                        'Año', 'Habitantes', '#2F7A6E', 1),
('GPC',                         'Generación per cápita',                   'Año', 'kg/hab/día', '#C98A1F', 2),
('generacion_bruta',            'Generación bruta total',                  'Año', 'ton/día',    '#C4502E', 3),
('Generacion_organicos',        'Generación de residuos orgánicos',        'Año', 'ton/día',    '#1D9E75', 4),
('Generacion_reciclables',      'Generación de residuos reciclables',      'Año', 'ton/día',    '#6F5BA8', 5),
('Generacion_no_aprovechables', 'Generación de residuos no aprovechables', 'Año', 'ton/día',    '#888780', 6);

INSERT INTO recoleccion_config (nivel, titulo, eje_x, eje_y, color, posicion) VALUES
('Residuos_dispersos',     'Residuos dispersos acumulados', 'Año', 'ton',        '#C4502E', 1),
('cobertura_recoleccion',  'Cobertura de recolección',      'Año', '%',          '#2F7A6E', 2),
('Compactadores',          'Flota: Compactadores',          'Año', 'unidades',   '#6F5BA8', 3),
('Volquetes',              'Flota: Volquetes',              'Año', 'unidades',   '#C98A1F', 4),
('Barandas',               'Flota: Barandas',               'Año', 'unidades',   '#1D9E75', 5),
('Flota_operativa',        'Flota operativa total',         'Año', 'unidades',   '#3A2E1F', 6);

INSERT INTO disposicion_config (nivel, titulo, eje_x, eje_y, color, posicion) VALUES
('Volumen_relleno_total',   'Volumen total en rellenos',     'Año', 'm³',        '#888780', 1),
('Volumen_Portillo',        'Relleno Portillo Grande',       'Año', 'm³',        '#C98A1F', 2),
('Volumen_Huaycoloro',      'Relleno Huaycoloro',            'Año', 'm³',        '#D85A30', 3),
('vida_util_remanente',     'Vida útil remanente',           'Año', 'años',      '#2F7A6E', 4),
('costo_unit_disposicion',  'Costo unitario de disposición', 'Año', 'US$/ton',   '#E24B4A', 5);

INSERT INTO valorizacion_config (nivel, titulo, eje_x, eje_y, color, posicion) VALUES
('Recicladores_formalizados', 'Recicladores formalizados',         'Año', 'personas',  '#6F5BA8', 1),
('valorizacion_total',        'Toneladas valorizadas',              'Año', 'ton/año',   '#1D9E75', 2),
('tasa_reciclaje',            'Tasa de reciclaje formal',           'Año', '%',         '#2F7A6E', 3),
('ingreso_reciclaje',         'Ingreso por reciclaje',              'Año', 'S//año',    '#C98A1F', 4),
('potencial_reciclaje',       'Potencial físico de reciclaje',      'Año', 'ton/año',   '#888780', 5),
('brecha_reciclaje',          'Brecha entre potencial y realidad',  'Año', 'ton/año',   '#C4502E', 6);

INSERT INTO financiamiento_config (nivel, titulo, eje_x, eje_y, color, posicion) VALUES
('Presupuesto_disponible',  'Presupuesto disponible',       'Año', 'S/',        '#2F7A6E', 1),
('Morosidad',               'Tasa de morosidad',            'Año', '%',         '#C4502E', 2),
('recaudacion_efectiva',    'Recaudación efectiva',         'Año', 'S//año',    '#C98A1F', 3),
('deficit_financiero',      'Déficit financiero',           'Año', 'S//año',    '#E24B4A', 4),
('presupuesto_per_capita',  'Presupuesto per cápita',       'Año', 'S//hab',    '#6F5BA8', 5);
```

---

## app.py — LÓGICA ESPERADA

```python
# Importa Flask, pyngrok, decouple
# Lee NGROK_TOKEN desde .env
# Inicia ngrok en el puerto 5000
# Registra las rutas desde route.py
# Corre la app Flask en debug=False, port=5000
```

---

## route.py — RUTAS EXACTAS

```python
# Ruta /  → renderiza landing.html (sin llamar al controlador)

# Rutas de subsistemas — todas siguen este patrón:
# 1. Llama a controller(subsistema) donde subsistema es el string exacto:
#    'generacion' | 'recoleccion' | 'disposicion' | 'valorizacion' | 'financiamiento'
# 2. Si el resultado contiene clave 'error' → renderiza error.html con el mensaje
# 3. Si no hay error → renderiza template.html pasando:
#    - niveles = resultado del controlador (diccionario con gráficas)
#    - subsistema = nombre legible ('Generación', 'Recolección', etc.)
#    - indicador = texto del indicador principal (ver tabla abajo)
#    - pestanas = lista de las 5 pestañas para construir la barra de navegación

# Tabla de indicadores por subsistema:
# generacion    → 'Generación per cápita (GPC) — kg/hab/día'
# recoleccion   → 'Cobertura de recolección — %'
# disposicion   → 'Vida útil remanente de rellenos — años'
# valorizacion  → 'Tasa de reciclaje formal — %'
# financiamiento→ 'Presupuesto per cápita — S/hab/año'
```

---

## controller.py — LÓGICA EXACTA

La función `controller(subsistema)` debe:

```python
# 1. Leer MDL_URL y MDL_FILENAME desde .env
#    — es UN SOLO archivo .mdl para todos los subsistemas

# 2. Descargar el archivo .mdl desde XAMPP con urllib3
#    — guardarlo en una carpeta local temporal (ej: /tmp/ o ./temp/)
#    — si falla la descarga → return {'error': 'No se pudo conectar al servidor XAMPP'}

# 3. Leer y simular el modelo con pysd:
#    modelo = pysd.read_vensim(ruta_local_mdl)
#    resultado_sim = modelo.run()
#    — si falla → return {'error': 'Error al simular el modelo Vensim'}

# 4. Consultar la tabla MySQL del subsistema correspondiente:
#    datos_bd = getModel<Subsistema>()   ← función del model.py
#    — si retorna error → return {'error': 'Error al conectar con la base de datos'}

# 5. Para cada fila de datos_bd:
#    a. Extraer el nombre del nivel (columna 'nivel')
#    b. Buscar ese nivel en resultado_sim (columnas del DataFrame de pysd)
#       — si no existe el nivel → return {'error': f'El nivel "{nivel}" no existe en el modelo'}
#    c. Crear figura matplotlib con:
#       - título = columna 'titulo' de la BD
#       - etiqueta eje X = columna 'eje_x'
#       - etiqueta eje Y = columna 'eje_y'
#       - color de línea = columna 'color'
#    d. Convertir a HTML interactivo con mpld3.fig_to_html(fig)
#    e. Guardar en diccionario: niveles[posicion] = {'titulo': ..., 'grafica': html_string}

# 6. Retornar el diccionario 'niveles' ordenado por 'posicion'
```

---

## model.py — FUNCIONES EXACTAS

Una función por subsistema. Todas siguen el mismo patrón:

```python
def getModelGeneracion():
    # connect() → si error → return {'error': '...'}
    # SELECT id, nivel, titulo, eje_x, eje_y, color, posicion
    # FROM generacion_config ORDER BY posicion ASC
    # connection_select(cursor, query)
    # cerrar cursor y conexión
    # return resultado

def getModelRecoleccion():    # FROM recoleccion_config
def getModelDisposicion():    # FROM disposicion_config
def getModelValorizacion():   # FROM valorizacion_config
def getModelFinanciamiento(): # FROM financiamiento_config

# Función genérica opcional (para no repetir):
def getModelBySubsistema(subsistema):
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
    # SELECT ... FROM {tabla} ORDER BY posicion ASC
```

---

## connection.py — SIN CAMBIOS RESPECTO AL MANUAL

```python
# connect():
#   mysql.connector.connect(
#     host=config('DB_HOST'), port=config('DB_PORT'),
#     user=config('DB_USER'), password=config('DB_PASSWORD'),
#     database=config('DB_NAME')
#   )
#   si error → return {'error': 'No se pudo conectar a MySQL'}
#   si ok    → return objeto conexión

# connection_select(cursorObject, select_stmt):
#   cursorObject.execute(select_stmt)
#   return cursorObject.fetchall()
```

---

## landing.html — CONTENIDO Y ESTRUCTURA

La landing page es la primera pantalla que ve el usuario. Debe tener:

```
[Barra superior con nombre del proyecto]

[Hero: título grande + descripción del proyecto en 2-3 líneas]
"Influencia del crecimiento poblacional y la capacidad financiera municipal
 sobre la gestión de residuos sólidos en San Juan de Lurigancho"

[5 tarjetas, una por subsistema — cada tarjeta tiene:]
  - Emoji o ícono representativo
  - Nombre del subsistema
  - Indicador principal (texto pequeño)
  - Botón o enlace → /generacion, /recoleccion, etc.

Tarjeta 1: Generación      → /generacion      → GPC (kg/hab/día)
Tarjeta 2: Recolección     → /recoleccion     → Cobertura de recolección (%)
Tarjeta 3: Disposición     → /disposicion     → Vida útil remanente (años)
Tarjeta 4: Valorización    → /valorizacion    → Tasa de reciclaje formal (%)
Tarjeta 5: Financiamiento  → /financiamiento  → Presupuesto per cápita (S/hab/año)

[Nota al pie: "Datos calibrados 2019–2023 · Proyección a 2040"]
```

---

## template.html — ESTRUCTURA DE LA VISTA DE SUBSISTEMA

```
[Barra de navegación fija — siempre visible]
  Tabs: Generación | Recolección | Disposición | Valorización | Financiamiento
  Tab activo = resaltado con color distinto
  Clic en cualquier tab → navega a esa ruta

[Encabezado de la vista]
  Título: nombre del subsistema
  Badge: texto del indicador principal

[Gráficas]
  — Para cada nivel en 'niveles' (ordenado por posicion):
    Mostrar el título de la gráfica
    Renderizar la gráfica (HTML de mpld3, insertar con {{ nivel.grafica | safe }})

[Enlace de retorno a la landing]
  "← Volver al inicio"

[Nota al pie con fuentes de datos]
```

---

## error.html — ESTRUCTURA

```
[Barra de navegación — igual que template.html]

[Icono de error visible]
[Mensaje de error: {{ mensaje }}]
[Explicación de posibles causas:]
  - El archivo .mdl no está en C:\xampp\htdocs\assets\vensim\
  - XAMPP no está corriendo (Apache o MySQL apagado)
  - El nombre del nivel en la BD no coincide con el modelo
  - Variables de entorno mal configuradas en .env

[Botón: "← Volver al inicio" → /]
```

---

## style.css — PALETA Y ESTILO

Usa estas variables de color exactas (son las del proyecto, definidas en conversación previa):

```css
:root {
  --tierra-900: #3A2E1F;  /* fondo topbar */
  --tierra-50:  #F7F3EC;  /* fondo general */
  --tierra-100: #EDE4D3;  /* bordes suaves */
  --teal-500:   #2F7A6E;  /* color principal activo */
  --teal-50:    #E6F2EF;  /* fondo badges */
  --alerta-500: #C4502E;  /* alertas / errores */
  --ambar-500:  #C98A1F;  /* advertencias */
  --linea:      #DDD3C2;  /* bordes generales */
  --texto-1:    #241D14;  /* texto principal */
  --texto-2:    #6E6253;  /* texto secundario */
  --texto-3:    #9C9181;  /* texto muted */
}
```

Reglas de estilo obligatorias:
- Topbar: fondo `--tierra-900`, texto blanco
- Tab activa: borde inferior `--teal-500`, texto `--teal-500`
- Tarjetas landing: fondo blanco, borde `--linea`, radio 10px
- Botón principal: fondo `--teal-500`, texto blanco
- Responsivo con CSS Grid o Flexbox, sin frameworks externos
- Las gráficas de mpld3 no necesitan estilos extra — se renderizan solas

---

## ORDEN DE IMPLEMENTACIÓN SUGERIDO

Trabaja en este orden para poder probar incrementalmente:

```
1. connection.py     ← probar que conecta a MySQL antes de tocar nada más
2. backup/vensimweb_sjl.sql  ← ejecutar en phpMyAdmin de XAMPP
3. model.py          ← probar que lee las tablas correctamente
4. controller.py     ← probar primero con el .mdl descargado manualmente
5. route.py          ← conectar rutas con controlador
6. app.py            ← levantar Flask y verificar http://127.0.0.1:5000/
7. landing.html      ← verificar que las 5 tarjetas enlazan bien
8. template.html     ← verificar que las gráficas se renderizan
9. error.html        ← probar renombrando el .mdl temporalmente
10. style.css        ← aplicar estilos finales
11. ngrok            ← configurar token y exponer al exterior
```

---

## MANEJO DE ERRORES — REGLAS

Todos los errores deben:
- Retornar un diccionario `{'error': 'mensaje descriptivo en español'}`
- Ser capturados en `route.py` y redirigir a `error.html`
- Indicar **qué falló específicamente** (no mensajes genéricos)

Errores mínimos obligatorios a manejar:

| Situación | Mensaje de error |
|---|---|
| XAMPP no corre / Apache caído | `No se pudo descargar el modelo. Verifica que XAMPP esté corriendo.` |
| Archivo .mdl no encontrado | `El archivo residuos_sjl.mdl no está en la ruta configurada en XAMPP.` |
| MySQL caído | `No se pudo conectar a la base de datos. Verifica que MySQL esté activo en XAMPP.` |
| Nombre de nivel incorrecto en BD | `El nivel "{nombre}" no existe en el modelo Vensim. Revisa la tabla {tabla}_config.` |
| Variables .env faltantes | `Variable de entorno {nombre} no configurada. Revisa el archivo .env.` |

---

## LO QUE NO DEBES HACER

- No crear archivos `.mdl` de prueba — ese archivo lo provee el equipo por separado
- No cambiar la estructura de carpetas definida arriba
- No usar frameworks CSS externos (Bootstrap, Tailwind) — solo el `style.css` del proyecto
- No crear una sola tabla MySQL para todos los subsistemas — son 5 tablas separadas
- No separar el `.mdl` en 5 archivos — es un único `residuos_sjl.mdl`
- No modificar la lógica de `connection.py` más allá de lo necesario para conectar
- No usar SQLite ni ninguna otra base de datos — solo MySQL vía XAMPP

---

## VERIFICACIÓN FINAL

Antes de considerar el proyecto terminado, verificar que:

- [ ] `http://127.0.0.1:5000/` muestra la landing page con las 5 tarjetas
- [ ] Cada tarjeta enlaza a su subsistema y muestra las gráficas correctas
- [ ] La barra de pestañas está visible en todas las vistas de subsistema
- [ ] La pestaña activa se distingue visualmente de las inactivas
- [ ] Renombrar `residuos_sjl.mdl` en XAMPP muestra `error.html` con mensaje claro
- [ ] Apagar MySQL en XAMPP muestra `error.html` con mensaje claro
- [ ] La página se ve bien en celular (responsive)
- [ ] ngrok genera una URL pública funcional
- [ ] Todas las gráficas tienen título, eje X y eje Y según la BD
- [ ] No hay errores en la consola de Python al navegar entre pestañas
