# Instrucciones Personalizadas para GitHub Copilot

## Contexto del Proyecto
Este es un sistema de gestión de flota de vehículos para la personería que incluye:
- Gestión completa de vehículos (CRUD)
- Administración de conductores
- Sistema de mantenimientos
- Procesamiento de solicitudes desde Excel
- Asignación inteligente de recursos
- Dashboard y reportes

## Tecnologías Principales
- **Backend**: FastAPI (Python) con SQLAlchemy
- **Frontend**: React + TypeScript + Redux
- **Base de Datos**: PostgreSQL/SQLite
- **Autenticación**: JWT
- **Procesamiento**: pandas, openpyxl para Excel

## Estilo de Código
- Usar typing hints en Python
- Documentar funciones y clases
- Seguir PEP 8 para Python
- Usar ESLint/Prettier para TypeScript
- Componentes funcionales en React

## Patrones de Desarrollo
- Repository pattern para acceso a datos
- Service layer para lógica de negocio
- DTO/Schema para transferencia de datos
- Hooks personalizados en React
- Estado global con Redux Toolkit

## Estructura de APIs
- RESTful endpoints
- Paginación en listados
- Filtros y búsquedas
- Manejo de errores consistente
- Documentación automática con FastAPI

## Validaciones
- Validar datos de entrada en backend
- Validaciones de formularios en frontend
- Constraints de BD apropiadas
- Manejo de errores usuario-friendly

## Seguridad
- Autenticación JWT
- Roles y permisos por módulo
- Sanitización de entradas
- Logging de acciones críticas