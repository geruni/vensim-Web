# Sistema de Gestión de Residuos Sólidos — San Juan de Lurigancho

Aplicación web que simula un modelo de Dinámica de Sistemas (Vensim) para la gestión de residuos sólidos en San Juan de Lurigancho, Lima, Perú.

## Requisitos previos

1. **Python 3.8+** instalado
2. **XAMPP** instalado y configurado:
   - Apache activo en el puerto 80
   - MySQL activo en el puerto 3306
3. **Archivo del modelo**: `residuos_sjl.mdl` ubicado en `C:\xampp\htdocs\assets\vensim\`

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

El sistema está dividido en 5 subsistemas:

1. **Generación** (`/generacion`) - GPC y generación de residuos por tipo
2. **Recolección** (`/recoleccion`) - Cobertura y flota de recolección
3. **Disposición** (`/disposicion`) - Rellenos sanitarios y vida útil
4. **Valorización** (`/valorizacion`) - Reciclaje y brecha de aprovechamiento
5. **Financiamiento** (`/financiamiento`) - Presupuesto y déficit financiero

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

- **Backend**: Flask (Python)
- **Simulación**: PySD
- **Gráficas**: Matplotlib + mpld3
- **Base de datos**: MySQL
- **Servidor**: XAMPP (Apache + MySQL)
- **Túnel público**: ngrok

## Autores

Universidad Nacional de Ingeniería - Dinámica de Sistemas
Proyecto: Gestión de Residuos Sólidos en San Juan de Lurigancho

---

**Datos calibrados 2019–2023 · Proyección a 2040**
"# vensim-Web" 
