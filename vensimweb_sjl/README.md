# Sistema de Gestión de Residuos Sólidos — San Juan de Lurigancho

Aplicación web que simula un modelo de Dinámica de Sistemas (Vensim) para la gestión de residuos sólidos en San Juan de Lurigancho, Lima, Perú.

## Requisitos previos

1. **Python 3.8+** instalado
2. **XAMPP** instalado y configurado:
   - Apache activo en el puerto 80
   - MySQL activo en el puerto 3306
3. **Archivo del modelo**: `residuos_sjl.mdl` ubicado en `C:\xampp\htdocs\assets\vensim\`
   - El archivo fuente se versiona en este repo en `../xampp_assets/residuos_sjl.mdl`. Cópialo a la ruta de XAMPP indicada arriba antes de levantar la app.

## Instalación

### 1. Instalar dependencias de Python

```bash
cd vensimweb_sjl
pip install -r requirements.txt
```

### 2. Configurar la base de datos

1. Abre **phpMyAdmin** en `http://localhost/phpmyadmin/`
2. Ve a la pestaña **Importar**
3. Selecciona el archivo `backup/vensimweb_sjl.sql`
4. Haz clic en **Continuar**

Esto creará la base de datos `vensimweb_sjl` con las 5 tablas necesarias y datos de ejemplo.

### 3. Configurar variables de entorno

Edita el archivo `.env` en la raíz del proyecto:

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

**Importante**:
- Si la base de datos MySQL tiene contraseña, especifícala en `DB_PASSWORD`
- Para usar ngrok (exponer la app públicamente), registra una cuenta gratuita en [ngrok.com](https://ngrok.com/) y coloca tu token en `NGROK_TOKEN`

### 4. Verificar que XAMPP está corriendo

Asegúrate de que:
- Apache está activo (luz verde en XAMPP)
- MySQL está activo (luz verde en XAMPP)
- El archivo `residuos_sjl.mdl` existe en `C:\xampp\htdocs\assets\vensim\`

## Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en:
- **Local**: `http://127.0.0.1:5000/`
- **Público** (si configuraste ngrok): La URL se mostrará en la consola

## Estructura del proyecto

```
vensimweb_sjl/
│
├── .env                          # Variables de entorno
├── requirements.txt              # Dependencias Python
├── app.py                        # Punto de entrada Flask
├── README.md                     # Este archivo
│
├── src/
│   ├── Routes/
│   │   └── route.py              # Rutas de la aplicación
│   ├── Controllers/
│   │   └── controller.py         # Lógica de negocio
│   ├── Models/
│   │   └── model.py              # Consultas a MySQL
│   └── Connection/
│       └── connection.py         # Conexión a base de datos
│
├── templates/
│   ├── landing.html              # Página de inicio
│   ├── template.html             # Plantilla de subsistemas
│   └── error.html                # Página de error
│
├── static/
│   └── css/
│       └── style.css             # Estilos del proyecto
│
└── backup/
    └── vensimweb_sjl.sql         # Respaldo de base de datos
```

## Subsistemas disponibles

El sistema está dividido en 5 subsistemas, cada uno con su propio panel en `/dashboard/<subsistema>`:

1. **Generación** (`/dashboard/generacion`) - GPC y generación de residuos por tipo
2. **Recolección** (`/dashboard/recoleccion`) - Cobertura y flota de recolección
3. **Disposición** (`/dashboard/disposicion`) - Rellenos sanitarios y vida útil
4. **Valorización** (`/dashboard/valorizacion`) - Reciclaje y brecha de aprovechamiento
5. **Financiamiento** (`/dashboard/financiamiento`) - Presupuesto y déficit financiero

## Panel de análisis interactivo

Cada subsistema abre un panel con gráficos interactivos (Plotly, incluido localmente
en `static/js/plotly.min.js`, sin necesidad de internet). Funciones:

- **Elegir niveles y subniveles** a graficar mediante casillas agrupadas (ej. la
  flota se desglosa en compactadores, volquetes y barandas).
- **Superponer** varias series en un mismo gráfico, con opción de **normalizar**
  (índice 100 en 2019) para comparar variables de distintas unidades de forma justa.
- **Real vs Simulado**: superpone los datos reales observados (2019–2023) sobre la
  curva simulada y muestra una tabla de comparación año por año con la diferencia
  porcentual y el **MAPE** (error porcentual absoluto medio) coloreado por nivel de ajuste.
- **Ratios A / B**: calcula y grafica el cociente entre cualquier par de variables
  del modelo a lo largo del horizonte.
- **Palancas de política (what-if)**: sliders para re-simular el modelo cambiando
  constantes clave (voluntad política de reciclaje, arbitrio por habitante,
  transferencias MEF, meta de cobertura, presupuesto de flota, tasa de natalidad).
  Al mover una palanca se superpone la corrida base punteada para dimensionar el
  efecto, y los escenarios guardados registran qué palancas se usaron.
- **KPIs** con el valor final, el cambio respecto a 2019, máximos y mínimos.
- **Guardar escenarios** simulados en la base de datos y superponerlos luego para comparar.
- **Exportar** el gráfico a PNG (barra de Plotly) o los datos a **CSV**.

### API JSON (para desarrolladores)

| Endpoint | Descripción |
|---|---|
| `GET /api/palancas` | Palancas what-if disponibles (nombre, rango, defecto) |
| `GET /api/series?niveles=a,b[&params=<json>]` | Series simuladas; `params` re-simula con palancas |
| `GET /api/comparar?subsistema=..&niveles=a,b[&params=<json>]` | Real vs simulado + diferencia, ratio y MAPE |
| `GET /api/ratio?a=..&b=..[&params=<json>]` | Serie del cociente A/B en el tiempo |
| `POST /api/guardar` | Guarda un escenario (`{nombre, descripcion, niveles, params}`) |
| `GET /api/escenarios` · `GET /api/escenario/<id>` | Lista / recupera escenarios guardados |

Las palancas se validan contra una lista blanca con rangos (`PALANCAS` en
`controller.py`); cualquier otro parámetro o valor fuera de rango se rechaza con 400.

## Base de datos

El script `backup/vensimweb_sjl.sql` crea:

- **5 tablas `*_config`** — configuración de cada gráfica (nivel, título, grupo, unidad, color).
- **`datos_reales`** — valores reales observados 2019–2023 (calibrados a referencias de
  SJL/PIGARS) para la comparación real vs simulado.
- **`simulaciones`** y **`simulacion_datos`** — escenarios simulados guardados desde el panel.

Los datos **simulados** se obtienen en vivo del modelo Vensim vía PySD; en la BD solo se
guardan la configuración visual, los datos reales y los escenarios que el usuario decida persistir.

## Solución de problemas

### Error: "No se pudo descargar el modelo"

- Verifica que XAMPP esté corriendo y Apache esté activo
- Verifica que el archivo `residuos_sjl.mdl` exista en `C:\xampp\htdocs\assets\vensim\`
- Verifica que `MDL_URL` en `.env` sea correcto

### Error: "No se pudo conectar a MySQL"

- Verifica que MySQL esté activo en XAMPP
- Verifica las credenciales en `.env` (usuario, contraseña, puerto)
- Verifica que la base de datos `vensimweb_sjl` exista

### Error: "El nivel X no existe en el modelo"

- El nombre del nivel en la base de datos no coincide con el modelo Vensim
- Verifica los nombres exactos en el archivo `.mdl`
- Actualiza la tabla correspondiente en MySQL

### ngrok no funciona

- Verifica que `NGROK_TOKEN` en `.env` contenga tu token real (no "TU_TOKEN_AQUI")
- Si no necesitas acceso público, puedes ignorar este error
- La aplicación funcionará localmente en `http://127.0.0.1:5000/`

## Tecnologías utilizadas

- **Backend**: Flask (Python) — patrón MVC + Route
- **Simulación**: PySD (lee y ejecuta el modelo Vensim `.mdl`)
- **Gráficas**: Plotly.js (interactivas, incluidas localmente)
- **Base de datos**: MySQL
- **Servidor**: XAMPP (Apache + MySQL)
- **Túnel público**: ngrok

## Autores

Universidad Nacional de Ingeniería - Dinámica de Sistemas
Proyecto: Gestión de Residuos Sólidos en San Juan de Lurigancho

---

**Datos calibrados 2019–2023 · Proyección a 2040**
"# vensim-Web" 
