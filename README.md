# 📋 Task Manager API

## 🚀 Descripción
API de gestión de tareas construida con FastAPI, que incluye autenticación OAuth2 con Google y GitHub.

## ✨ Características
- 👤 Autenticación de usuarios (local y OAuth2)
- 🔐 Integración con Google y GitHub
- ✅ CRUD completo de tareas
- 📱 API RESTful
- 🔒 Seguridad JWT
- 🗄️ Base de datos SQLite (desarrollo) y PostgreSQL (producción)

## 🛠️ Tecnologías
- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker
- OAuth2

## 🚀 Instalación y Uso

### 🐳 Con Docker

#### Desarrollo
```bash
ENV=development docker compose --profile dev up --build
```

#### Producción
```bash
ENV= docker compose --profile prod up --build
```

### 🔧 Instalación Local
1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
```

2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Instalar dependencias
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno
- Copiar `.env.example` a `.env.development` para desarrollo
- Copiar `.env.example` a `.env` para producción
- Configurar las variables necesarias

5. Ejecutar la aplicación
```bash
# Desarrollo
uvicorn app.main:app --reload

# Producción
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📚 Documentación API
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔑 Endpoints Principales

### 👤 Usuarios
- POST `/register` - Registro de usuario
- POST `/token` - Login y obtención de token
- GET `/auth/google/login` - Login con Google
- GET `/auth/github/login` - Login con GitHub

### ✅ Tareas
- GET `/tasks` - Listar tareas
- POST `/tasks` - Crear tarea
- GET `/tasks/{id}` - Obtener tarea
- PUT `/tasks/{id}` - Actualizar tarea
- DELETE `/tasks/{id}` - Eliminar tarea
- PATCH `/tasks/{id}/complete` - Marcar tarea como completada

## 🔐 Variables de Entorno
- `ENV` - Entorno (development/production)
- `SECRET_KEY` - Clave secreta para JWT
- `DATABASE_URL` - URL de la base de datos
- `GOOGLE_CLIENT_ID` - ID de cliente de Google
- `GITHUB_CLIENT_ID` - ID de cliente de GitHub
- Y otras variables de configuración...

## 👥 Contribución
1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/NuevaCaracteristica`)
3. Commit de cambios (`git commit -am 'Añadir nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Crear Pull Request

## 📝 Licencia
Este proyecto está bajo la Licencia MIT
```