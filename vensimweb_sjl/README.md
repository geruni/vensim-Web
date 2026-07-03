# Sistema de Gestion de Residuos Solidos - San Juan de Lurigancho

Aplicacion web que simula un modelo de Dinamica de Sistemas (Vensim) para la gestion de residuos solidos en San Juan de Lurigancho, Lima, Peru.

## Requisitos previos

1. **Python 3.8+** instalado

Ya no se necesita XAMPP, MySQL ni ngrok: la base de datos es un archivo SQLite
autogenerado y el modelo Vensim (`model/residuos_sjl.mdl`) se lee directo del disco.

## Instalacion

### 1. Instalar dependencias de Python

```bash
cd vensimweb_sjl
pip install -r requirements.txt
```

### 2. Base de datos

No requiere ningun paso manual: al arrancar, `app.py` llama a `db/init_db.py`, que crea
`db/vensimweb_sjl.db` (SQLite) con las 5 tablas de configuracion y los datos reales
2019-2023, si el archivo todavia no existe. Para forzar recrearla desde cero:

```bash
python db/init_db.py --force
```

### 3. Variables de entorno (opcionales)

No hace falta `.env` para correr localmente: los valores por defecto ya apuntan a
`db/vensimweb_sjl.db` y `model/residuos_sjl.mdl` dentro del proyecto. Solo crea un `.env`
(ver `.env.example`) si quieres usar otra ruta para la BD o el `.mdl`.

## Ejecutar la aplicacion

```bash
python app.py
```

La aplicacion estara disponible en `http://127.0.0.1:5000/`.

En produccion (Render) se usa `gunicorn` en vez de `app.run()` - ver `Procfile`.

## Estructura del proyecto

```
vensimweb_sjl/
|
|-- .env.example                  # Variables de entorno (opcionales)
|-- requirements.txt              # Dependencias Python
|-- Procfile                      # Comando de arranque para Render (gunicorn)
|-- app.py                        # Punto de entrada Flask
|-- README.md                     # Este archivo
|
|-- model/
|   `-- residuos_sjl.mdl          # Modelo Vensim vendorizado (se lee del disco)
|
|-- db/
|   |-- schema.sql                # Esquema SQLite + datos reales de fabrica
|   |-- init_db.py                # Crea/recrea vensimweb_sjl.db
|   `-- vensimweb_sjl.db          # (generado; no se versiona)
|
|-- src/
|   |-- Routes/
|   |   `-- route.py              # Rutas de la aplicacion
|   |-- Controllers/
|   |   `-- controller.py         # Logica de negocio + simulacion PySD
|   |-- Models/
|   |   `-- model.py              # Consultas a SQLite
|   `-- Connection/
|       `-- connection.py         # Conexion a base de datos (SQLite)
|
|-- templates/
|   |-- landing.html              # Pagina de inicio
|   |-- template.html             # Plantilla de subsistemas
|   `-- error.html                # Pagina de error
|
|-- static/
|   `-- css/
|       `-- style.css             # Estilos del proyecto
|
`-- backup/
    `-- vensimweb_sjl.sql         # Script original en MySQL (historico, ya no se usa)
```

## Subsistemas disponibles

El sistema esta dividido en 5 subsistemas, cada uno con su propio panel en `/dashboard/<subsistema>`:

1. **Generacion** (`/dashboard/generacion`) - GPC y generacion de residuos por tipo
2. **Recoleccion** (`/dashboard/recoleccion`) - Cobertura y flota de recoleccion
3. **Disposicion** (`/dashboard/disposicion`) - Rellenos sanitarios y vida util
4. **Valorizacion** (`/dashboard/valorizacion`) - Reciclaje y brecha de aprovechamiento
5. **Financiamiento** (`/dashboard/financiamiento`) - Presupuesto y deficit financiero

## Panel de analisis interactivo

Cada subsistema abre un panel con graficos interactivos (Plotly, incluido localmente
en `static/js/plotly.min.js`, sin necesidad de internet). Funciones:

- **Elegir niveles y subniveles** a graficar mediante casillas agrupadas (ej. la
  flota se desglosa en compactadores, volquetes y barandas).
- **Superponer** varias series en un mismo grafico, con opcion de **normalizar**
  (indice 100 en 2019) para comparar variables de distintas unidades de forma justa.
- **Real vs Simulado**: superpone los datos reales observados (2019-2023) sobre la
  curva simulada y muestra una tabla de comparacion ano por ano con la diferencia
  porcentual y el **MAPE** (error porcentual absoluto medio) coloreado por nivel de ajuste.
- **Ratios A / B**: calcula y grafica el cociente entre cualquier par de variables
  del modelo a lo largo del horizonte.
- **Palancas de politica (what-if)**: sliders para re-simular el modelo cambiando
  constantes clave (voluntad politica de reciclaje, arbitrio por habitante,
  transferencias MEF, meta de cobertura, presupuesto de flota, tasa de natalidad).
  Al mover una palanca se superpone la corrida base punteada para dimensionar el
  efecto, y los escenarios guardados registran que palancas se usaron.
- **KPIs** con el valor final, el cambio respecto a 2019, maximos y minimos.
- **Guardar escenarios** simulados en la base de datos y superponerlos luego para comparar.
- **Exportar** el grafico a PNG (barra de Plotly) o los datos a **CSV**.

### API JSON (para desarrolladores)

| Endpoint | Descripcion |
|---|---|
| `GET /api/palancas` | Palancas what-if disponibles (nombre, rango, defecto) |
| `GET /api/series?niveles=a,b[&params=<json>]` | Series simuladas; `params` re-simula con palancas |
| `GET /api/comparar?subsistema=..&niveles=a,b[&params=<json>]` | Real vs simulado + diferencia, ratio y MAPE |
| `GET /api/ratio?a=..&b=..[&params=<json>]` | Serie del cociente A/B en el tiempo |
| `POST /api/guardar` | Guarda un escenario (`{nombre, descripcion, niveles, params}`) |
| `GET /api/escenarios` / `GET /api/escenario/<id>` | Lista / recupera escenarios guardados |

Las palancas se validan contra una lista blanca con rangos (`PALANCAS` en
`controller.py`); cualquier otro parametro o valor fuera de rango se rechaza con 400.

## Base de datos

`db/schema.sql` (aplicado por `db/init_db.py`) crea:

- **5 tablas `*_config`** - configuracion de cada grafica (nivel, titulo, grupo, unidad, color).
- **`datos_reales`** - valores reales observados 2019-2023 (calibrados a referencias de
  SJL/PIGARS) para la comparacion real vs simulado.
- **`simulaciones`** y **`simulacion_datos`** - escenarios simulados guardados desde el panel.

Los datos **simulados** se obtienen en vivo del modelo Vensim via PySD; en la BD solo se
guardan la configuracion visual, los datos reales y los escenarios que el usuario decida persistir.

**Nota sobre persistencia en Render (tier gratis)**: el disco del free tier no esta
garantizado entre deploys/reinicios. Cada build corre `python db/init_db.py --force`,
asi que la app siempre arranca con la configuracion y los datos reales de fabrica; los
escenarios que un usuario guarde durante la sesion pueden perderse si la instancia se
reinicia o se hace un nuevo deploy. Si mas adelante quieres persistencia garantizada,
hay que pasar a un plan pagado con disco persistente o a una base de datos gestionada
(Postgres, por ejemplo).

## Solucion de problemas

### Error: "No se encontro el archivo del modelo Vensim"

- Verifica que exista `model/residuos_sjl.mdl` en el proyecto
- Si usas una ruta distinta, definela en `.env` con `MDL_PATH`

### Error: "No se encontro la base de datos SQLite"

- Ejecuta `python db/init_db.py` para crearla
- Si usas una ruta distinta, definela en `.env` con `DB_PATH`

### Error: "El nivel X no existe en el modelo"

- El nombre del nivel en la base de datos no coincide con el modelo Vensim
- Verifica los nombres exactos en el archivo `.mdl`
- Actualiza la tabla correspondiente en `db/schema.sql` y vuelve a correr `init_db.py --force`

## Tecnologias utilizadas

- **Backend**: Flask (Python) - patron MVC + Route, servido con `gunicorn` en produccion
- **Simulacion**: PySD (lee y ejecuta el modelo Vensim `.mdl`)
- **Graficas**: Plotly.js (interactivas, incluidas localmente)
- **Base de datos**: SQLite (archivo local, sin servicio aparte)
- **Hosting**: Render (free tier)

## Autores

Universidad Nacional de Ingenieria - Dinamica de Sistemas
Proyecto: Gestion de Residuos Solidos en San Juan de Lurigancho

---

**Datos calibrados 2019-2023 - Proyeccion a 2040**
