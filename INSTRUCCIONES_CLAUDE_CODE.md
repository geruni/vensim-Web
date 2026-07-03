# Documentación técnica del proyecto (v2)
## Sistema de Gestión de Residuos Sólidos — San Juan de Lurigancho
## Aplicación web que simula un modelo Vensim y lo explora en un panel interactivo

> **Nota de versión.** Este documento reemplaza la especificación original (v1) con la
> que se construyó el primer prototipo. El proyecto evolucionó: las gráficas estáticas
> de matplotlib+mpld3 fueron reemplazadas por un panel interactivo con Plotly.js, se
> agregaron datos observados, palancas de política (what-if) y escenarios guardados.
> La sección final resume qué cambió respecto a la v1.

---

## CONTEXTO DEL PROYECTO

Tarea universitaria de **Dinámica de Sistemas** (Universidad Nacional de Ingeniería,
Lima, Perú). Toma un modelo de simulación hecho en Vensim (`.mdl`) y lo expone en una
página web que cualquier persona puede abrir desde su celular o laptop, sin instalar nada.

El modelo simula la **gestión de residuos sólidos en San Juan de Lurigancho**
(~1.2 millones de habitantes) con 5 subsistemas: Generación, Recolección,
Disposición final, Valorización y Financiamiento. 132 variables, 14 niveles (stocks),
horizonte 2019–2040, paso 0.25 años.

---

## DECISIONES VIGENTES

1. **Un solo archivo `.mdl`** (`residuos_sjl.mdl`) con los 5 subsistemas. El archivo
   fuente se versiona en `xampp_assets/` y en producción vive en
   `C:\xampp\htdocs\assets\vensim\residuos_sjl.mdl`.
2. **Flask** (Python) con arquitectura **MVC + Route** (`src/Routes`, `src/Controllers`,
   `src/Models`, `src/Connection`).
3. **XAMPP** (Apache + MySQL) como servidor local; **ngrok** para exponer la app.
4. **PySD** lee y simula el `.mdl`. La simulación se **cachea en memoria** por
   (hash del `.mdl`, parámetros); si el archivo cambia, el caché se invalida solo.
5. **Plotly.js incluido localmente** (`static/js/plotly.min.js`) para gráficos
   interactivos — sin CDNs, funciona sin internet. (Reemplaza a matplotlib + mpld3.)
6. **MySQL** guarda: configuración visual de gráficas (5 tablas `*_config`), datos
   reales observados (`datos_reales`) y escenarios simulados guardados
   (`simulaciones` + `simulacion_datos`). Los resultados de simulación NO se
   guardan salvo que el usuario persista un escenario.
7. **Las gráficas de Generación apuntan a los flujos** (`entrada generacion bruta`,
   `gen organicos`, `gen reciclables`, `gen no aprovechables`), no a los
   niveles-stock del patrón ómnibus/taxis/motos, porque esos niveles tienen
   entrada = salida y quedan congelados en su valor inicial.
8. La brecha de valorización se reporta con la variable real del modelo
   **`Discrep reciclaje`** (`max(0, potencial reciclaje − valorizacion total)`).
9. Los nombres de nivel en la BD usan **espacios** (como el `.mdl`), p. ej.
   `cobertura recoleccion`, no `cobertura_recoleccion`.

---

## ESTRUCTURA DE CARPETAS

```
vensim-Web/
├── INSTRUCCIONES_CLAUDE_CODE.md   # este documento
├── xampp_assets/
│   └── residuos_sjl.mdl           # modelo Vensim (copiar a C:\xampp\htdocs\assets\vensim\)
└── vensimweb_sjl/
    ├── .env / .env.example        # variables de entorno
    ├── requirements.txt           # flask, pyngrok, pysd, mysql-connector-python,
    │                              # python-decouple, numpy, urllib3
    ├── app.py                     # punto de entrada: Flask + ngrok
    ├── verificar_instalacion.py   # chequeo previo de entorno
    ├── src/
    │   ├── Routes/route.py        # vistas + API JSON
    │   ├── Controllers/controller.py  # simulación PySD, series, comparación, ratios, palancas
    │   ├── Models/model.py        # consultas y escritura MySQL
    │   └── Connection/connection.py   # conexión y helpers
    ├── templates/
    │   ├── landing.html           # landing animada
    │   ├── dashboard.html         # panel de análisis por subsistema
    │   └── error.html             # errores amigables
    ├── static/
    │   ├── css/style.css          # estilos del panel
    │   ├── css/landing.css        # estilos de la landing
    │   ├── js/app.js              # lógica del panel
    │   ├── js/landing.js          # animaciones de la landing
    │   └── js/plotly.min.js       # Plotly local
    └── backup/vensimweb_sjl.sql   # esquema + seed completo (hace DROP y recrea)
```

---

## BASE DE DATOS (`backup/vensimweb_sjl.sql`)

El script crea la BD `vensimweb_sjl` (utf8mb4) y **recrea las tablas desde cero**
(hace `DROP TABLE IF EXISTS`): al reimportar se pierden los escenarios guardados.

**5 tablas de configuración** — `generacion_config`, `recoleccion_config`,
`disposicion_config`, `valorizacion_config`, `financiamiento_config`:

| Columna | Uso |
|---|---|
| `nivel` | Nombre EXACTO de la variable en el `.mdl` (con espacios) |
| `titulo`, `grupo` | Título de la gráfica y grupo del selector (ej. "Flota", "Por tipo") |
| `eje_x`, `eje_y`, `unidad` | Etiquetas y unidad |
| `color`, `posicion` | Color de la serie y orden |

**`datos_reales`** — valores observados 2019–2023 por (subsistema, nivel, anio),
con columna `fuente`. Alimenta el modo "Real vs Simulado" (125 filas seed).

**`simulaciones`** — escenarios guardados: `nombre`, `descripcion`,
`parametros` (JSON de palancas usadas, NULL si es corrida base), `creado`.
**`simulacion_datos`** — series del escenario (FK con `ON DELETE CASCADE`).

---

## BACKEND — API JSON

| Endpoint | Descripción |
|---|---|
| `GET /` | Landing |
| `GET /dashboard/<subsistema>` | Panel del subsistema (`generacion`, `recoleccion`, `disposicion`, `valorizacion`, `financiamiento`) |
| `GET /api/palancas` | Palancas what-if disponibles (nombre, rango, paso, defecto) |
| `GET /api/series?niveles=a,b[&params=<json>]` | Series simuladas; `params` re-simula con palancas |
| `GET /api/comparar?subsistema=..&niveles=..[&params=..]` | Real vs simulado + diferencia, ratio y MAPE por nivel |
| `GET /api/ratio?a=..&b=..[&params=..]` | Cociente A/B en el tiempo |
| `POST /api/guardar` | Guarda escenario `{nombre, descripcion, niveles, params}` |
| `GET /api/escenarios` | Lista escenarios (incluye `parametros`) |
| `GET /api/escenario/<id>` | Series de un escenario guardado |
| `DELETE /api/escenario/<id>` | Elimina un escenario |

**Palancas what-if (lista blanca en `controller.py`)** — solo estas constantes del
modelo pueden modificarse, con rango validado en el servidor (400 si es inválido):

| Palanca | Rango | Defecto | Subsistema |
|---|---|---|---|
| `voluntad politica` | 0 – 1 | 0.5 | Valorización |
| `arbitrio por habitante` | 60 – 240 | 120 | Financiamiento |
| `transferencias MEF` | 0 – 60 M | 18 M | Financiamiento |
| `Obj cobertura` | 0.5 – 1 | 0.9 | Recolección |
| `fracc presupuesto flota` | 0.05 – 0.40 | 0.18 | Recolección |
| `tasa natalidad` | 0.010 – 0.025 | 0.018 | Generación |

---

## FRONTEND — PANEL (`dashboard.html` + `app.js`)

Cuatro modos de análisis:

1. **Superponer** — varias series en un lienzo; opción de normalizar (índice 100
   en 2019). Con palancas activas superpone la corrida base punteada.
2. **Real vs Simulado** — puntos observados sobre la curva simulada + tabla año a
   año con Δ% y MAPE coloreado (verde ≤10%, ámbar ≤25%, rojo >25%).
3. **Ratio A / B** — cociente entre cualquier par de variables del catálogo.
4. **Escenarios A vs B** — compara dos escenarios guardados (o uno contra la
   corrida base): A sólida vs B discontinua, KPIs 2040 y tabla de diferencias.

Transversales: sliders de palancas con re-render automático (debounce), guardar /
eliminar escenarios, exportar CSV y PNG, KPIs con cambio vs 2019.

## FRONTEND — LANDING (`landing.html` + `landing.css` + `landing.js`)

Hero oscuro con partículas en canvas y revelado escalonado; diagrama del sistema
en SVG con flujos animados y pulsos viajeros; contadores animados; tarjetas por
subsistema con **sparklines vivas** (consultan `/api/series`; se ocultan con
elegancia si la API no responde); respeta `prefers-reduced-motion`.

---

## MANEJO DE ERRORES

- Toda falla del backend retorna `{'error': 'mensaje descriptivo en español'}`.
- Las vistas renderizan `error.html`; la API responde JSON con código 4xx/5xx y
  el frontend lo muestra como toast.
- Errores cubiertos: XAMPP/Apache caído (descarga del `.mdl`), error de PySD,
  MySQL caído, nivel inexistente en el modelo, `.env` incompleto, palanca fuera
  de rango o no permitida.

---

## PUESTA EN MARCHA

1. `pip install -r requirements.txt`
2. Copiar `xampp_assets/residuos_sjl.mdl` a `C:\xampp\htdocs\assets\vensim\`
3. Encender Apache y MySQL en XAMPP
4. Importar `backup/vensimweb_sjl.sql` en phpMyAdmin (reimportar tras cada cambio de esquema)
5. Copiar `.env.example` a `.env` y ajustar credenciales / token de ngrok
6. `python verificar_instalacion.py` (opcional) y `python app.py`
7. Abrir `http://127.0.0.1:5000/` — la primera carga tarda más (PySD traduce el `.mdl`)

---

## CAMBIOS RESPECTO A LA ESPECIFICACIÓN ORIGINAL (v1)

| v1 (spec original) | v2 (implementado) | Motivo |
|---|---|---|
| Gráficas matplotlib + mpld3 renderizadas en servidor | Plotly.js local + API JSON | Interactividad (zoom, hover, superponer) y menos carga por request |
| `template.html` con gráficas fijas por subsistema | `dashboard.html` con 4 modos de análisis | Elegir niveles, comparar, ratios, escenarios |
| Nombres de nivel con guion bajo (`generacion_bruta`) | Nombres con espacios, idénticos al `.mdl` | PySD expone las columnas con los nombres originales |
| Nivel `brecha_reciclaje` | `Discrep reciclaje` | `brecha_reciclaje` no existe en el `.mdl` entregado |
| Gráficas de Generación sobre los niveles-stock | Sobre los flujos (`gen organicos`, …) | Los stocks del patrón ómnibus/taxis/motos quedan congelados (entrada = salida) |
| Solo 5 tablas `*_config` | + `datos_reales`, `simulaciones`, `simulacion_datos` | Comparación real vs simulado y escenarios guardados |
| Landing con tarjetas estáticas | Landing animada con datos vivos del modelo | Calidad de presentación |

> **Nota sobre `datos_reales`:** los 125 valores observados son estimaciones
> sintéticas calibradas alrededor de la simulación (desviaciones deterministas);
> las etiquetas de `fuente` son referenciales. Si se requieren cifras oficiales,
> reemplazar las series y sus fuentes.

---

## VERIFICACIÓN

- [ ] `/` muestra la landing con sparklines en las 5 tarjetas
- [ ] Cada pestaña del panel grafica sus niveles y el tab activo se distingue
- [ ] Modo Real vs Simulado muestra puntos, tabla y MAPE
- [ ] Mover una palanca re-simula y superpone la corrida base punteada
- [ ] Guardar escenario lo registra (⚙ si tiene palancas) y "Escenarios A vs B" lo compara
- [ ] Eliminar un escenario pide confirmación y lo quita de la lista
- [ ] Renombrar el `.mdl` en XAMPP o apagar MySQL muestra errores claros
- [ ] Exportar CSV y PNG funciona en todos los modos
- [ ] La página se ve bien en celular
- [ ] ngrok genera URL pública funcional
