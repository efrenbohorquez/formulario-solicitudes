# Estructura del Proyecto

Esta es la estructura principal del sistema de gestión de flota de vehículos:

```
formulario-solicitudes/
├── backend/                   # API Backend (FastAPI)
│   ├── app/                   # Aplicación principal
│   │   ├── api/               # Endpoints API
│   │   │   └── v1/            # Versión 1 de la API
│   │   │       └── endpoints/ # Controladores específicos
│   │   ├── core/              # Configuración principal
│   │   ├── database/          # Configuración de base de datos
│   │   ├── models/            # Modelos SQLAlchemy
│   │   ├── schemas/           # Esquemas Pydantic
│   │   └── services/          # Lógica de negocio
│   ├── logs/                  # Archivos de registro
│   └── uploads/               # Archivos subidos
│       ├── documents/         # Documentos
│       ├── excel/             # Archivos Excel procesados
│       └── images/            # Imágenes de vehículos
│
├── frontend/                  # Interfaz de usuario (Pendiente)
│
├── docs/                      # Documentación del proyecto
│   ├── MANUAL_COMPLETO.md     # Manual completo del sistema
│   ├── DOCUMENTACION_TECNICA.md # Documentación técnica
│   ├── GUIA_RAPIDA.md         # Guía rápida de uso
│   ├── INSTALACION.md         # Guía de instalación
│   └── INDICE_DOCUMENTACION.md # Índice de documentación
│
├── README.md                  # Información principal del proyecto
├── CHANGELOG.md               # Registro de cambios
├── ESTADO_PROYECTO.md         # Estado actual del desarrollo
├── LICENSE                    # Licencia del software
└── .gitignore                 # Archivos ignorados por Git
```

## Descripción de Directorios

### `/backend/`
Contiene toda la lógica del servidor backend desarrollado con FastAPI:
- **`app/api/`**: Endpoints REST organizados por versión
- **`app/core/`**: Configuración, autenticación y utilidades centrales
- **`app/database/`**: Configuración de la base de datos SQLite/PostgreSQL
- **`app/models/`**: Modelos de datos usando SQLAlchemy ORM
- **`app/schemas/`**: Esquemas de validación con Pydantic
- **`app/services/`**: Servicios de negocio (procesamiento Excel, notificaciones)

### `/frontend/` (Pendiente de desarrollo)
Destinado para la interfaz de usuario web desarrollada en React + TypeScript

### `/docs/`
Documentación completa del proyecto:
- Manuales de usuario y administrador
- Documentación técnica para desarrolladores
- Guías de instalación y configuración
- Referencias de API

## Archivos de Configuración

- **`requirements.txt`**: Dependencias de Python
- **`fleet_management.db`**: Base de datos SQLite local
- **`init_db.py`**: Script de inicialización de la base de datos
- **`start.bat/start.sh`**: Scripts de inicio del servidor

## Próximos Directorios (Roadmap)

```
mobile/                        # Aplicación móvil (React Native)
tests/                         # Pruebas automatizadas
docker/                        # Configuración Docker
deployment/                    # Scripts de despliegue
config/                        # Archivos de configuración por entorno
```

Para más información, consulta el [Manual Completo](MANUAL_COMPLETO.md) o la [Guía Rápida](GUIA_RAPIDA.md).