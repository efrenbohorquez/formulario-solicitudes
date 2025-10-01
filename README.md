# Sistema de Gestión de Flota - Personería

Sistema web completo para la gestión de vehículos, conductores y mantenimientos de la flota de transporte de la personería.

## Características Principales

### 🚗 Gestión de Vehículos
- CRUD completo de vehículos
- Información técnica, documentos y estado
- Control de disponibilidad
- Historial de uso y mantenimiento

### 👨‍💼 Gestión de Conductores  
- CRUD de conductores
- Gestión de licencias y certificaciones
- Control de disponibilidad y horarios
- Historial de servicios

### 🔧 Sistema de Mantenimientos
- Programación de mantenimientos preventivos
- Registro de mantenimientos correctivos
- Control de costos y proveedores
- Alertas y notificaciones

### 📋 Gestión de Solicitudes
- Importación desde archivos Excel
- Asignación automática e inteligente
- Seguimiento en tiempo real
- Reportes y métricas

### 📊 Dashboard y Reportes
- Panel principal con métricas
- Reportes operativos y administrativos
- Análisis de uso y costos
- Exportación de datos

## Arquitectura Técnica

**Backend:** FastAPI (Python)
- API REST moderna y rápida
- Documentación automática
- Validación de datos

**Frontend:** React + TypeScript
- Interfaz moderna y responsiva
- Componentes reutilizables
- Estado global con Redux

**Base de Datos:** SQLite/PostgreSQL
- Modelos relacionales
- Migrations automáticas
- Respaldos programados

**Autenticación:** JWT
- Roles y permisos
- Sesiones seguras
- Control de acceso

## Estructura del Proyecto

```
/
├── backend/               # API FastAPI
│   ├── app/
│   │   ├── models/       # Modelos de BD
│   │   ├── schemas/      # Esquemas Pydantic
│   │   ├── crud/         # Operaciones BD
│   │   ├── api/          # Endpoints API
│   │   ├── core/         # Configuración
│   │   └── utils/        # Utilidades
│   ├── alembic/          # Migrations
│   └── requirements.txt
├── frontend/             # React App
│   ├── src/
│   │   ├── components/   # Componentes React
│   │   ├── pages/        # Páginas principales
│   │   ├── services/     # Servicios API
│   │   ├── store/        # Estado Redux
│   │   └── utils/        # Utilidades
│   ├── public/
│   └── package.json
└── docs/                 # Documentación

```

## Instalación y Uso

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## Funcionalidades por Módulo

### Vehículos
- Registro completo (placa, marca, modelo, año, etc.)
- Documentos (SOAT, tecnomecánica, seguros)
- Estados (disponible, en uso, mantenimiento, fuera de servicio)
- Tracking GPS (opcional)

### Conductores
- Información personal y profesional
- Licencias y certificaciones
- Experiencia y calificaciones
- Disponibilidad y horarios
- Historial de infracciones

### Mantenimientos
- Programación automática por kilometraje/tiempo
- Registro de servicios realizados
- Control de garantías
- Gestión de proveedores
- Alertas preventivas

### Solicitudes y Asignaciones
- Importación masiva desde Excel
- Algoritmos de asignación inteligente
- Validación de disponibilidad
- Optimización de rutas
- Notificaciones automáticas

## Estados del Sistema

- **Desarrollo Activo** 🔄
- Versión: 1.0.0
- Última actualización: Septiembre 2025