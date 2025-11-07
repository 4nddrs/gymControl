# Gym Control - Sistema de Gestión de Gimnasio

Sistema web desarrollado con Flask para la gestión completa de un gimnasio.

## 🏋️‍♂️ Características

- 👥 Gestión de usuarios y miembros
- 🔐 Control de acceso biométrico
- 💳 Administración de membresías
- 📊 Reportes y estadísticas
- 📸 Gestión de fotos de usuarios
- 🔍 Búsqueda y filtrado avanzado

## 🚀 Instalación

### 1. Activar entorno virtual

```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crear archivo `.env` con:

```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=tu_clave_secreta_aqui
MONGO_URI=mongodb://localhost:27017/
DATABASE_NAME=gimnasio_db
```

### 4. Ejecutar la aplicación

```powershell
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

## 📁 Estructura del Proyecto

```
gymControl/
├── app.py                  # Aplicación principal
├── config.py              # Configuración
├── requirements.txt       # Dependencias
├── .env                   # Variables de entorno
├── venv/                  # Entorno virtual
├── models/                # Modelos de datos
├── routes/                # Rutas/Endpoints
├── templates/             # Templates HTML
├── static/                # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── img/
└── utils/                 # Utilidades
```

## 🛠️ Tecnologías

- **Backend**: Flask (Python)
- **Base de Datos**: MongoDB
- **Frontend**: HTML, CSS, JavaScript
- **Plantillas**: Jinja2

## 📝 Endpoints Principales

- `/` - Dashboard principal
- `/usuarios` - Gestión de usuarios
- `/membresias` - Gestión de membresías
- `/asistencias` - Control de asistencias
- `/biometria` - Gestión biométrica
- `/reportes` - Reportes y estadísticas

## 🔒 Seguridad

- Variables de entorno para credenciales
- Validación de datos
- Sanitización de inputs
- Protección CSRF

## 👨‍💻 Desarrollo

Activar modo debug en `.env`:

```
FLASK_ENV=development
FLASK_DEBUG=1
```

## 📄 Licencia

Proyecto privado para uso interno del gimnasio.
