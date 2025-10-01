# Backend - Sistema de Gestión de Flota

API REST desarrollada con FastAPI para el sistema de gestión de flota vehicular de la personería.

## 🚀 Características

- **Gestión completa de vehículos** - CRUD con estados, documentación y historial
- **Administración de conductores** - Licencias, disponibilidad y asignaciones
- **Sistema de mantenimientos** - Programación, costos y alertas automáticas
- **Procesamiento de solicitudes Excel** - Importación y validación de datos
- **Asignación inteligente** - Verificación de disponibilidad y conflictos
- **Dashboard completo** - Métricas, estadísticas y reportes
- **Autenticación JWT** - Roles y permisos granulares
- **Alertas automáticas** - Vencimientos y mantenimientos programados

## 🛠️ Tecnologías

- **FastAPI** 0.104.1 - Framework web moderno y rápido
- **SQLAlchemy** 2.0.23 - ORM y gestión de base de datos
- **Pydantic** 2.5.0 - Validación de datos y serialización
- **JWT** - Autenticación y autorización
- **APScheduler** - Tareas programadas y alertas
- **Pandas/OpenPyXL** - Procesamiento de archivos Excel

## 📦 Instalación

### 1. Clonar y navegar al proyecto
```bash
cd "formulario solicitudes/backend"
```

### 2. Crear entorno virtual
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
# Copiar archivo de ejemplo
copy .env.example .env

# Editar .env con tu configuración
notepad .env
```

### 5. Inicializar base de datos
```bash
python init_db.py
```

### 6. Iniciar servidor de desarrollo
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 URLs Importantes

- **API**: http://localhost:8000
- **Documentación interactiva**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔐 Autenticación

### Credenciales por defecto
- **Usuario**: `admin`
- **Contraseña**: `admin123`
- ⚠️ **Cambiar inmediatamente en producción**

### Roles disponibles
- **ADMIN** - Acceso completo al sistema
- **SUPERVISOR** - Gestión de operaciones y reportes
- **USUARIO** - Consultas y operaciones básicas

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/          # Endpoints de la API
│   │       │   ├── vehicles.py     # Gestión de vehículos
│   │       │   ├── drivers.py      # Gestión de conductores
│   │       │   ├── maintenance.py  # Sistema de mantenimientos
│   │       │   ├── requests.py     # Solicitudes de transporte
│   │       │   ├── assignments.py  # Asignaciones y viajes
│   │       │   ├── dashboard.py    # Dashboard y estadísticas
│   │       │   ├── auth.py         # Autenticación y usuarios
│   │       │   └── alerts.py       # Alertas y notificaciones
│   │       └── api.py              # Router principal
│   ├── core/
│   │   ├── config.py               # Configuración de la app
│   │   └── database.py             # Configuración de BD
│   ├── database/
│   │   └── models.py               # Modelos SQLAlchemy
│   ├── schemas/
│   │   └── schemas.py              # Esquemas Pydantic
│   ├── services/
│   │   ├── excel_processor.py      # Procesamiento Excel
│   │   ├── notification_service.py # Sistema de notificaciones
│   │   └── scheduler.py            # Tareas programadas
│   └── main.py                     # Punto de entrada
├── logs/                           # Archivos de log
├── uploads/                        # Archivos subidos
├── requirements.txt                # Dependencias Python
├── init_db.py                      # Script de inicialización
└── .env.example                    # Variables de entorno ejemplo
```

## 🔧 API Endpoints

### Autenticación
- `POST /api/v1/auth/token` - Obtener token JWT
- `POST /api/v1/auth/register` - Registrar usuario (admin)
- `GET /api/v1/auth/me` - Información del usuario actual

### Vehículos
- `GET /api/v1/vehicles/` - Listar vehículos
- `POST /api/v1/vehicles/` - Crear vehículo
- `GET /api/v1/vehicles/{id}` - Obtener vehículo específico
- `PUT /api/v1/vehicles/{id}` - Actualizar vehículo
- `DELETE /api/v1/vehicles/{id}` - Eliminar vehículo

### Conductores
- `GET /api/v1/drivers/` - Listar conductores
- `POST /api/v1/drivers/` - Crear conductor
- `GET /api/v1/drivers/{id}` - Obtener conductor específico
- `PUT /api/v1/drivers/{id}` - Actualizar conductor

### Mantenimientos
- `GET /api/v1/maintenance/` - Listar mantenimientos
- `POST /api/v1/maintenance/` - Programar mantenimiento
- `PUT /api/v1/maintenance/{id}` - Actualizar mantenimiento

### Solicitudes
- `GET /api/v1/requests/` - Listar solicitudes
- `POST /api/v1/requests/` - Crear solicitud
- `POST /api/v1/requests/upload-excel` - Procesar Excel

### Asignaciones
- `GET /api/v1/assignments/` - Listar asignaciones
- `POST /api/v1/assignments/` - Crear asignación
- `POST /api/v1/assignments/{id}/start-trip` - Iniciar viaje
- `POST /api/v1/assignments/{id}/end-trip` - Finalizar viaje

### Dashboard
- `GET /api/v1/dashboard/stats` - Estadísticas generales
- `GET /api/v1/dashboard/alerts` - Alertas importantes
- `GET /api/v1/dashboard/vehicle-availability` - Disponibilidad de flota

### Alertas
- `GET /api/v1/alerts/` - Listar alertas
- `POST /api/v1/alerts/check-expired-documents` - Verificar vencimientos
- `POST /api/v1/alerts/check-maintenance-due` - Verificar mantenimientos

## 🔄 Tareas Automáticas

El sistema ejecuta tareas programadas para:
- ✅ Verificar vencimientos de documentos (SOAT, técnico-mecánica)
- ✅ Alertar sobre licencias de conducir próximas a vencer
- ✅ Notificar mantenimientos por kilometraje
- ✅ Enviar notificaciones por email
- ✅ Limpiar registros antiguos

## 📊 Base de Datos

### SQLite (Desarrollo)
```bash
# Base de datos local automática
DATABASE_URL="sqlite:///./fleet_management.db"
```

### PostgreSQL (Producción)
```bash
# Instalar PostgreSQL y crear base de datos
createdb fleet_management

# Configurar en .env
DATABASE_URL="postgresql://usuario:contraseña@localhost/fleet_management"
```

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app tests/
```

## 🚀 Despliegue

### Docker (Recomendado)
```bash
# Construir imagen
docker build -t fleet-management-api .

# Ejecutar contenedor
docker run -p 8000:8000 fleet-management-api
```

### Servidor tradicional
```bash
# Producción con Gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## 📝 Variables de Entorno

### Básicas
- `DATABASE_URL` - URL de conexión a base de datos
- `SECRET_KEY` - Clave secreta para JWT (cambiar en producción)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Duración del token en minutos

### Email/Notificaciones
- `EMAIL_HOST` - Servidor SMTP
- `EMAIL_USER` - Usuario del email
- `EMAIL_PASSWORD` - Contraseña del email
- `FROM_EMAIL` - Email remitente

### Alertas
- `MAINTENANCE_KM_INTERVAL` - Intervalo de km para mantenimiento
- `DOCUMENT_EXPIRY_WARNING_DAYS` - Días de anticipación para alertas

## 🔍 Monitoreo y Logs

```bash
# Ver logs en tiempo real
tail -f logs/app.log

# Verificar estado de la API
curl http://localhost:8000/health
```

## 🛠️ Comandos Útiles

```bash
# Reiniciar base de datos
python init_db.py

# Ejecutar verificación manual de alertas
curl -X POST "http://localhost:8000/api/v1/alerts/check-expired-documents"

# Backup de base de datos SQLite
copy fleet_management.db fleet_management_backup.db
```

## 🆘 Troubleshooting

### Error de conexión a BD
```bash
# Verificar que la BD existe y es accesible
python -c "from app.core.database import engine; print(engine.url)"
```

### Problemas con dependencias
```bash
# Reinstalar dependencias
pip install --upgrade -r requirements.txt
```

### Token expirado
```bash
# Obtener nuevo token
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

## 📚 Documentación Adicional

- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [JWT.io](https://jwt.io/)

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👥 Autor

Sistema desarrollado para la Personería - Gestión de Flota Vehicular