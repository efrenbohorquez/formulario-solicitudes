# 📚 MANUAL COMPLETO DEL SISTEMA DE GESTIÓN DE FLOTA
## PERSONERÍA MUNICIPAL

---

## 📋 TABLA DE CONTENIDOS

1. [Introducción](#introducción)
2. [Instalación y Configuración](#instalación-y-configuración)
3. [Guía de Usuario](#guía-de-usuario)
4. [Manual del Administrador](#manual-del-administrador)
5. [API Reference](#api-reference)
6. [Solución de Problemas](#solución-de-problemas)
7. [Anexos](#anexos)

---

## 🎯 INTRODUCCIÓN

### ¿Qué es el Sistema de Gestión de Flota?

El **Sistema de Gestión de Flota** es una aplicación web integral diseñada específicamente para la Personería Municipal que permite:

- ✅ **Gestionar vehículos** de manera centralizada
- ✅ **Administrar conductores** y sus licencias
- ✅ **Programar y seguir mantenimientos**
- ✅ **Procesar solicitudes** desde archivos Excel
- ✅ **Asignar recursos** de forma inteligente
- ✅ **Generar reportes** y estadísticas
- ✅ **Recibir alertas** automáticas

### Características Principales

| Módulo | Funcionalidad |
|--------|---------------|
| 🚗 **Vehículos** | CRUD, estados, documentación, historial |
| 👨‍✈️ **Conductores** | Licencias, disponibilidad, asignaciones |
| 🔧 **Mantenimientos** | Programación, costos, alertas automáticas |
| 📊 **Dashboard** | Métricas en tiempo real, KPIs |
| 🔔 **Alertas** | Vencimientos, mantenimientos programados |
| 📱 **Mobile Ready** | Interfaz optimizada para dispositivos móviles |

---

## ⚙️ INSTALACIÓN Y CONFIGURACIÓN

### Requisitos del Sistema

#### Hardware Mínimo
- **CPU**: 2 cores, 2.0 GHz
- **RAM**: 4 GB
- **Almacenamiento**: 10 GB libres
- **Red**: Conexión a internet (para alertas por email)

#### Software Requerido
- **Sistema Operativo**: Windows 10/11, Ubuntu 18+, macOS 10.15+
- **Python**: 3.8 o superior
- **Navegador**: Chrome 90+, Firefox 88+, Safari 14+

### Instalación Paso a Paso

#### 1. Descargar el Código
```bash
# Ubicar el proyecto en:
C:\Users\[usuario]\formulario solicitudes\
```

#### 2. Instalar Python y Dependencias
```bash
# Verificar Python
python --version

# Navegar al directorio
cd "C:\Users\efren\formulario solicitudes\backend"

# Instalar dependencias básicas
pip install fastapi uvicorn sqlalchemy pydantic-settings python-multipart
pip install passlib python-jose bcrypt python-decouple email-validator 
pip install python-dotenv APScheduler
```

#### 3. Configurar Variables de Entorno
```bash
# Copiar archivo de configuración
copy .env.example .env

# Editar configuración (usar notepad o editor preferido)
notepad .env
```

#### 4. Inicializar Base de Datos
```bash
# Ejecutar script de inicialización
python init_db.py
```

#### 5. Iniciar el Sistema
```bash
# Opción 1: Script automatizado
start.bat

# Opción 2: Manual
uvicorn app.main:app --reload --port 8000
```

### Configuración Avanzada

#### Base de Datos PostgreSQL (Producción)
```env
DATABASE_URL=postgresql://usuario:contraseña@localhost/fleet_management
```

#### Configuración de Email
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=sistema@personeria.gov.co
EMAIL_PASSWORD=tu_contraseña_app
FROM_EMAIL=sistema@personeria.gov.co
```

#### Configuración de Seguridad
```env
SECRET_KEY=tu_clave_super_secreta_de_64_caracteres_cambiar_en_produccion
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

---

## 👥 GUÍA DE USUARIO

### Acceso al Sistema

#### Iniciar Sesión
1. Abrir navegador web
2. Ir a: http://localhost:8000
3. Hacer clic en "Documentación" o ir a /docs
4. Usar credenciales por defecto:
   - **Usuario**: `admin`
   - **Contraseña**: `admin123`

### Panel Principal (Dashboard)

#### Vista General
El dashboard muestra información clave de la flota:

```
┌─────────────────────────────────────────┐
│              RESUMEN FLOTA              │
├─────────────────┬───────────────────────┤
│ Total Vehículos │ 15                    │
│ Disponibles     │ 8                     │
│ En Uso          │ 5                     │
│ Mantenimiento   │ 2                     │
├─────────────────┼───────────────────────┤
│ Total Conduct.  │ 12                    │
│ Disponibles     │ 7                     │
│ En Servicio     │ 5                     │
├─────────────────┼───────────────────────┤
│ Solicitudes     │ 3 pendientes          │
│ Alertas Activas │ 2 críticas           │
└─────────────────┴───────────────────────┘
```

#### Alertas Importantes
- 🔴 **Críticas**: Documentos vencidos, mantenimientos urgentes
- 🟡 **Altas**: Vencimientos próximos (7-15 días)
- 🟢 **Medias**: Recordatorios generales (15-30 días)

### Gestión de Vehículos

#### Agregar Nuevo Vehículo
1. Ir a **Vehículos** → **Nuevo**
2. Completar formulario:
   - **Placa** (obligatorio): ABC123
   - **Marca/Modelo**: Toyota Corolla
   - **Año**: 2020
   - **Tipo**: Sedan/SUV/Camioneta/Bus
   - **Color**: Blanco
   - **Número de Motor**: 123456789

#### Documentación del Vehículo
- **SOAT**: Fecha de vencimiento
- **Revisión Técnico-Mecánica**: Fecha de vencimiento
- **Tarjeta de Propiedad**: Número y fecha
- **Póliza de Seguros**: Compañía y vigencia

#### Estados del Vehículo
- 🟢 **Disponible**: Listo para asignación
- 🔵 **En Uso**: Asignado a un viaje
- 🟡 **Mantenimiento**: En reparación/servicio
- 🔴 **Fuera de Servicio**: No operativo

### Gestión de Conductores

#### Registro de Conductor
1. Ir a **Conductores** → **Nuevo**
2. Datos personales:
   - **Nombre Completo**: Juan Pérez García
   - **Cédula**: 12345678
   - **Teléfono**: 300-123-4567
   - **Email**: juan.perez@personeria.gov.co
   - **Dirección**: Calle 123 #45-67

#### Información de Licencia
- **Número de Licencia**: 987654321
- **Categoría**: B1, B2, C1, etc.
- **Fecha de Vencimiento**: DD/MM/AAAA
- **Años de Experiencia**: Número

#### Estados del Conductor
- 🟢 **Disponible**: Puede ser asignado
- 🔵 **En Servicio**: Realizando viaje
- 🟡 **Descanso**: En horario de descanso
- 🔴 **Incapacitado**: Temporal o permanentemente

### Sistema de Mantenimientos

#### Programar Mantenimiento
1. Seleccionar vehículo
2. Tipo de mantenimiento:
   - **Preventivo**: Rutinario (aceite, filtros)
   - **Correctivo**: Reparaciones específicas
   - **Emergencia**: Urgente por falla
   - **Revisión Técnica**: Inspección oficial

#### Seguimiento de Costos
- **Costo Estimado**: Presupuesto inicial
- **Costo Real**: Gasto final
- **Repuestos**: Lista de piezas utilizadas
- **Proveedor**: Taller o mecánico

### Procesamiento de Solicitudes

#### Importar desde Excel
1. Ir a **Solicitudes** → **Importar Excel**
2. Seleccionar archivo .xlsx/.xls
3. Verificar formato:
   ```
   | Nombre | Dependencia | Fecha | Origen | Destino | Pasajeros |
   |--------|-------------|-------|--------|---------|-----------|
   | Juan   | Jurídica    | 15/10 | Sede   | Juzgado | 2         |
   ```
4. Confirmar importación

#### Gestión Manual de Solicitudes
- **Datos del Solicitante**: Nombre, dependencia, contacto
- **Detalles del Viaje**: Fecha, hora, origen, destino
- **Requerimientos**: Número de pasajeros, tipo de vehículo
- **Prioridad**: Baja/Media/Alta/Crítica

### Sistema de Asignaciones

#### Asignación Automática
El sistema sugiere automáticamente:
- Vehículo disponible más adecuado
- Conductor disponible con licencia vigente
- Verificación de conflictos de horarios

#### Asignación Manual
1. Seleccionar solicitud pendiente
2. Elegir vehículo y conductor
3. Confirmar asignación
4. Sistema valida disponibilidad

#### Seguimiento de Viajes
- **Inicio de Viaje**: Registrar kilometraje inicial
- **Finalización**: Kilometraje final, observaciones
- **Calificación**: Evaluación del servicio (1-5 estrellas)

---

## 👨‍💼 MANUAL DEL ADMINISTRADOR

### Gestión de Usuarios

#### Crear Nuevo Usuario
```http
POST /api/v1/auth/register
{
  "username": "nuevo_usuario",
  "email": "usuario@personeria.gov.co",
  "nombre_completo": "Nombre Apellido",
  "password": "contraseña_segura",
  "rol": "supervisor"
}
```

#### Roles y Permisos

| Rol | Permisos |
|-----|----------|
| **ADMIN** | Acceso total, crear usuarios, configuración |
| **SUPERVISOR** | Gestión operativa, reportes, asignaciones |
| **USUARIO** | Consultas, solicitudes básicas |

### Configuración del Sistema

#### Parámetros de Alertas
```env
# Configuración de alertas automáticas
MAINTENANCE_KM_INTERVAL=10000          # Mantenimiento cada 10,000 km
MAINTENANCE_ALERT_KM_THRESHOLD=1000    # Alertar 1,000 km antes
DOCUMENT_EXPIRY_WARNING_DAYS=30        # Alertar 30 días antes
DOCUMENT_CRITICAL_WARNING_DAYS=7       # Crítico a 7 días
```

#### Programación de Tareas Automáticas
- **Verificación de vencimientos**: Diaria a las 8:00 AM
- **Alertas de mantenimiento**: Cada 6 horas
- **Notificaciones por email**: Inmediatas
- **Limpieza de logs**: Semanal

### Backup y Seguridad

#### Backup Automático
```bash
# Backup diario de base de datos
copy fleet_management.db backup\fleet_management_2025-10-01.db

# Script de backup automatizado
backup_database.bat
```

#### Configuración de Seguridad
- **JWT Tokens**: Expiración en 24 horas
- **Contraseñas**: Mínimo 8 caracteres, hash bcrypt
- **CORS**: Configurado para dominios específicos
- **Logs**: Registro de todas las operaciones críticas

### Monitoreo y Reportes

#### Métricas Clave (KPIs)
1. **Utilización de Flota**: % de vehículos en uso
2. **Tiempo de Respuesta**: Promedio de asignación
3. **Costo por Kilómetro**: Eficiencia económica
4. **Disponibilidad**: % de vehículos operativos
5. **Satisfacción**: Calificación promedio de servicios

#### Reportes Disponibles
- 📊 **Reporte de Utilización**: Uso por vehículo/período
- 💰 **Reporte de Costos**: Gastos de mantenimiento
- 🔧 **Reporte de Mantenimientos**: Historial completo
- 📈 **Dashboard Ejecutivo**: Métricas consolidadas

---

## 🔌 API REFERENCE

### Autenticación

#### Obtener Token de Acceso
```http
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "username": "admin",
    "nombre_completo": "Administrador"
  }
}
```

### Endpoints de Vehículos

#### Listar Vehículos
```http
GET /api/v1/vehicles?page=1&limit=20&estado=disponible

Response:
{
  "items": [
    {
      "id": 1,
      "placa": "ABC123",
      "marca": "Toyota",
      "modelo": "Corolla",
      "estado": "disponible",
      "kilometraje": 45000
    }
  ],
  "total": 15,
  "page": 1,
  "pages": 1
}
```

#### Crear Vehículo
```http
POST /api/v1/vehicles
Content-Type: application/json
Authorization: Bearer {token}

{
  "placa": "XYZ789",
  "marca": "Chevrolet",
  "modelo": "Spark",
  "año": 2021,
  "tipo_vehiculo": "sedan",
  "color": "Blanco"
}
```

### Endpoints de Dashboard

#### Estadísticas Generales
```http
GET /api/v1/dashboard/stats

Response:
{
  "total_vehiculos": 15,
  "vehiculos_disponibles": 8,
  "vehiculos_en_uso": 5,
  "vehiculos_mantenimiento": 2,
  "total_conductores": 12,
  "conductores_disponibles": 7,
  "solicitudes_pendientes": 3,
  "alertas_activas": 2
}
```

### Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| 200 | Operación exitosa |
| 201 | Recurso creado exitosamente |
| 400 | Error en datos de entrada |
| 401 | No autorizado (token inválido) |
| 403 | Prohibido (sin permisos) |
| 404 | Recurso no encontrado |
| 422 | Error de validación |
| 500 | Error interno del servidor |

---

## 🛠️ SOLUCIÓN DE PROBLEMAS

### Problemas Comunes

#### 1. El servidor no inicia
**Síntoma**: Error al ejecutar `uvicorn app.main:app`
```bash
# Verificar instalación
python --version
pip list | grep fastapi

# Reinstalar dependencias
pip install --upgrade fastapi uvicorn
```

#### 2. Error de conexión a base de datos
**Síntoma**: `database.db locked`
```bash
# Verificar procesos
tasklist | findstr python

# Terminar procesos Python
taskkill /f /im python.exe

# Reiniciar servidor
python init_db.py
```

#### 3. Token JWT expirado
**Síntoma**: `401 Unauthorized`
```http
# Obtener nuevo token
POST /api/v1/auth/token
```

#### 4. Problemas de CORS
**Síntoma**: Error en navegador web
```python
# Verificar configuración en main.py
allow_origins=["*"]  # Para desarrollo
allow_origins=["https://mi-dominio.com"]  # Para producción
```

### Logs y Diagnóstico

#### Ubicación de Logs
- **Aplicación**: `logs/app.log`
- **Uvicorn**: Terminal/consola
- **Base de Datos**: `logs/database.log`

#### Comandos de Diagnóstico
```bash
# Ver logs en tiempo real
tail -f logs/app.log

# Verificar estado de la API
curl http://localhost:8000/health

# Test de conectividad
ping localhost

# Verificar puerto
netstat -an | findstr :8000
```

### Recuperación de Datos

#### Backup de Emergencia
```bash
# Crear backup manual
copy fleet_management.db backup/emergency_backup.db

# Restaurar desde backup
copy backup/fleet_management_2025-10-01.db fleet_management.db
```

#### Reset Completo del Sistema
```bash
# ⚠️ CUIDADO: Esto borra todos los datos
del fleet_management.db
python init_db.py
```

---

## 📎 ANEXOS

### Anexo A: Formatos de Archivo Excel

#### Plantilla de Solicitudes
```excel
| A: Nombre Solicitante | B: Dependencia | C: Fecha Viaje | D: Hora | E: Origen | F: Destino | G: Pasajeros | H: Observaciones |
|----------------------|----------------|----------------|---------|-----------|------------|--------------|------------------|
| Juan Pérez           | Jurídica       | 15/10/2025     | 14:00   | Sede      | Juzgado    | 2            | Urgente          |
| María García         | Contabilidad   | 16/10/2025     | 09:30   | Oficina   | Banco      | 1            |                  |
```

### Anexo B: Códigos de Error

| Código | Descripción | Solución |
|--------|-------------|----------|
| VH001 | Placa duplicada | Verificar placa existente |
| DR002 | Licencia vencida | Actualizar fecha de licencia |
| AS003 | Conflicto de horarios | Verificar disponibilidad |
| MN004 | Mantenimiento obligatorio | Programar servicio |

### Anexo C: Variables de Configuración

```env
# Base de datos
DATABASE_URL=sqlite:///./fleet_management.db

# Seguridad
SECRET_KEY=clave_super_secreta_de_64_caracteres
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=sistema@personeria.gov.co
EMAIL_PASSWORD=contraseña_aplicacion

# Alertas
MAINTENANCE_KM_INTERVAL=10000
DOCUMENT_EXPIRY_WARNING_DAYS=30

# Archivos
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=.xlsx,.xls,.csv

# API
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

### Anexo D: Comandos de Mantenimiento

```bash
# Verificar estado del sistema
python -c "from app.main import app; print('OK')"

# Limpiar logs antiguos
forfiles /p logs /s /m *.log /d -30 /c "cmd /c del @path"

# Optimizar base de datos
sqlite3 fleet_management.db "VACUUM;"

# Verificar integridad
sqlite3 fleet_management.db "PRAGMA integrity_check;"

# Estadísticas de uso
sqlite3 fleet_management.db "SELECT COUNT(*) FROM vehicles;"
```

---

## 📞 SOPORTE TÉCNICO

### Contacto
- **Email**: soporte@personeria.gov.co
- **Teléfono**: (1) 123-456-7890
- **Horario**: Lunes a Viernes, 8:00 AM - 5:00 PM

### Recursos Adicionales
- 📖 **Documentación**: http://localhost:8000/docs
- 🐛 **Reportar Bugs**: Crear issue en el repositorio
- 💡 **Sugerencias**: Contactar al equipo de desarrollo
- 🎓 **Capacitación**: Solicitar sesión de entrenamiento

---

**© 2025 Personería Municipal - Sistema de Gestión de Flota v1.0.0**