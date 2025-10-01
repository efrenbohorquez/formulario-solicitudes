# 📋 GUÍA RÁPIDA DE USUARIO
## Sistema de Gestión de Flota

---

## 🚀 INICIO RÁPIDO

### 1. Acceso al Sistema
1. **Abrir navegador web** (Chrome, Firefox, Edge)
2. **Ir a**: http://localhost:8000
3. **Hacer clic**: "Ver Documentación" → `/docs`
4. **Iniciar sesión**:
   - Usuario: `admin`
   - Contraseña: `admin123`

### 2. Panel Principal
```
📊 DASHBOARD - VISTA GENERAL
┌────────────────────────────────────┐
│ Total Vehículos:  15 🚗            │
│ Disponibles:       8 🟢            │
│ En Uso:            5 🔵            │
│ Mantenimiento:     2 🟡            │
├────────────────────────────────────┤
│ Conductores:      12 👨‍✈️            │
│ Solicitudes:       3 📋            │
│ Alertas:           2 ⚠️             │
└────────────────────────────────────┘
```

---

## 🚗 GESTIÓN DE VEHÍCULOS

### ➕ Agregar Vehículo
1. **Ir a**: `POST /api/v1/vehicles`
2. **Completar datos**:
```json
{
  "placa": "ABC123",
  "marca": "Toyota",
  "modelo": "Corolla",
  "año": 2020,
  "tipo_vehiculo": "sedan",
  "color": "Blanco",
  "kilometraje": 45000
}
```

### 📋 Consultar Vehículos
```http
GET /api/v1/vehicles
GET /api/v1/vehicles/{id}
GET /api/v1/vehicles/available
```

### ✏️ Actualizar Estado
```http
PUT /api/v1/vehicles/{id}/estado
{
  "estado": "disponible" | "en_uso" | "mantenimiento"
}
```

### 📊 Estados de Vehículo
| Estado | Descripción | Color |
|--------|-------------|-------|
| **Disponible** | Listo para asignar | 🟢 Verde |
| **En Uso** | Realizando viaje | 🔵 Azul |
| **Mantenimiento** | En servicio | 🟡 Amarillo |
| **Fuera de Servicio** | No operativo | 🔴 Rojo |

---

## 👨‍✈️ GESTIÓN DE CONDUCTORES

### ➕ Registrar Conductor
```json
{
  "cedula": "12345678",
  "nombre_completo": "Juan Pérez García",
  "telefono": "300-123-4567",
  "email": "juan.perez@personeria.gov.co",
  "licencia_numero": "987654321",
  "licencia_categoria": "B1",
  "licencia_vencimiento": "2026-12-31",
  "años_experiencia": 5
}
```

### 📱 Endpoints Principales
```http
POST   /api/v1/drivers           # Crear conductor
GET    /api/v1/drivers           # Listar todos
GET    /api/v1/drivers/{id}      # Ver específico
PUT    /api/v1/drivers/{id}      # Actualizar
GET    /api/v1/drivers/available # Disponibles
```

### 🏷️ Estados del Conductor
- 🟢 **Disponible**: Puede ser asignado
- 🔵 **En Servicio**: Realizando viaje
- 🟡 **Descanso**: En horario de descanso
- 🔴 **Incapacitado**: No puede conducir

---

## 🔧 SISTEMA DE MANTENIMIENTOS

### 📅 Programar Mantenimiento
```json
{
  "vehicle_id": 1,
  "tipo": "preventivo",
  "descripcion": "Cambio de aceite y filtros",
  "fecha_programada": "2025-10-15",
  "kilometraje_programado": 55000,
  "costo_estimado": 150000,
  "proveedor": "Taller Central"
}
```

### 🛠️ Tipos de Mantenimiento
| Tipo | Descripción | Frecuencia |
|------|-------------|------------|
| **Preventivo** | Rutinario (aceite, filtros) | 10,000 km |
| **Correctivo** | Reparaciones específicas | Según falla |
| **Emergencia** | Urgente por avería | Inmediato |
| **Revisión Técnica** | Inspección oficial | Anual |

### 📊 Seguimiento de Costos
```json
{
  "costo_estimado": 150000,
  "costo_real": 180000,
  "repuestos": [
    {"nombre": "Filtro aceite", "costo": 25000},
    {"nombre": "Aceite 20W50", "costo": 85000}
  ],
  "mano_obra": 70000
}
```

---

## 📋 SOLICITUDES DE TRANSPORTE

### 📥 Crear Solicitud Manual
```json
{
  "solicitante_nombre": "María García",
  "solicitante_dependencia": "Jurídica",
  "solicitante_telefono": "300-987-6543",
  "fecha_viaje": "2025-10-15",
  "hora_salida": "14:00",
  "origen": "Sede Principal",
  "destino": "Juzgado Civil",
  "numero_pasajeros": 2,
  "observaciones": "Diligencia urgente"
}
```

### 📊 Importar desde Excel
1. **Endpoint**: `POST /api/v1/requests/import-excel`
2. **Formato requerido**:
```excel
| Nombre | Dependencia | Fecha | Hora | Origen | Destino | Pasajeros |
|--------|-------------|-------|------|--------|---------|-----------|
| Juan   | Jurídica    | 15/10 | 14:00| Sede   | Juzgado | 2         |
| María  | Contable    | 16/10 | 09:30| Oficina| Banco   | 1         |
```

### 🔍 Consultar Solicitudes
```http
GET /api/v1/requests?page=1&limit=20
GET /api/v1/requests?estado=pendiente
GET /api/v1/requests?fecha=2025-10-15
```

---

## 🎯 SISTEMA DE ASIGNACIONES

### ⚡ Asignación Automática
El sistema sugiere automáticamente:
- ✅ Vehículo disponible más adecuado
- ✅ Conductor con licencia vigente
- ✅ Sin conflictos de horarios

### 📝 Crear Asignación
```json
{
  "request_id": 1,
  "vehicle_id": 3,
  "driver_id": 2,
  "fecha_asignacion": "2025-10-15T14:00:00",
  "observaciones": "Asignación automática"
}
```

### 📊 Estados de Asignación
- 🟡 **Programada**: Asignada, no iniciada
- 🔵 **En Curso**: Viaje en progreso
- 🟢 **Completada**: Viaje finalizado
- 🔴 **Cancelada**: Asignación cancelada

### ✅ Completar Viaje
```json
{
  "kilometraje_final": 150,
  "hora_llegada": "16:30",
  "observaciones": "Viaje completado sin novedad",
  "calificacion": 5
}
```

---

## 📈 DASHBOARD Y REPORTES

### 📊 Estadísticas Generales
```http
GET /api/v1/dashboard/stats

Response:
{
  "total_vehiculos": 15,
  "vehiculos_disponibles": 8,
  "vehiculos_en_uso": 5,
  "total_conductores": 12,
  "conductores_disponibles": 7,
  "solicitudes_pendientes": 3,
  "alertas_activas": 2
}
```

### 🎯 KPIs Principales
```http
GET /api/v1/dashboard/kpis

Response:
{
  "utilizacion_flota": 67.5,          # % vehículos en uso
  "tiempo_respuesta_promedio": 2.5,    # horas
  "costo_por_kilometro": 850,         # pesos
  "disponibilidad": 87.3,             # % operativos
  "satisfaccion_promedio": 4.2        # calificación
}
```

---

## 🔔 SISTEMA DE ALERTAS

### ⚠️ Tipos de Alertas

#### 🔴 Críticas (Acción Inmediata)
- Documentos vencidos
- Mantenimientos obligatorios
- Vehículos averiados

#### 🟡 Altas (7-15 días)
- Vencimientos próximos
- Mantenimientos programados
- Licencias por vencer

#### 🟢 Medias (15-30 días)
- Recordatorios generales
- Revisiones programadas

### 📋 Consultar Alertas
```http
GET /api/v1/alerts                    # Todas
GET /api/v1/alerts/critical           # Solo críticas
GET /api/v1/alerts?tipo=documento     # Por tipo
```

### 📧 Configurar Notificaciones
```json
{
  "email_alertas": true,
  "email_mantenimientos": true,
  "email_vencimientos": true,
  "frecuencia": "diaria"
}
```

---

## 🔐 AUTENTICACIÓN

### 🔑 Obtener Token de Acceso
```http
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

**Respuesta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 🎭 Roles y Permisos

| Rol | Permisos |
|-----|----------|
| **ADMIN** | 🟢 Todo: crear usuarios, configurar sistema |
| **SUPERVISOR** | 🟡 Operativo: gestión, reportes, asignaciones |
| **USUARIO** | 🔵 Básico: consultas, solicitudes propias |

### 🔒 Usar Token en Requests
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## 🚨 SOLUCIÓN RÁPIDA DE PROBLEMAS

### ❌ Error 401 - No autorizado
**Causa**: Token expirado o inválido
**Solución**: Obtener nuevo token en `/auth/token`

### ❌ Error 400 - Datos inválidos
**Causa**: Formato de datos incorrecto
**Solución**: Verificar schema en documentación `/docs`

### ❌ Error 500 - Error del servidor
**Causa**: Problema interno del sistema
**Solución**: 
1. Verificar logs en `logs/app.log`
2. Reiniciar servidor: `uvicorn app.main:app --reload`

### 🔧 Comandos de Diagnóstico
```bash
# Verificar API
curl http://localhost:8000/health

# Ver logs en tiempo real
tail -f logs/app.log

# Reiniciar servidor
cd backend && uvicorn app.main:app --reload --port 8000
```

---

## 📚 RECURSOS ADICIONALES

### 🔗 Enlaces Útiles
- **Documentación API**: http://localhost:8000/docs
- **API Alternativa**: http://localhost:8000/redoc
- **Estado del Sistema**: http://localhost:8000/health

### 📞 Soporte
- **Email**: soporte@personeria.gov.co
- **Teléfono**: (1) 123-456-7890
- **Horario**: Lunes a Viernes, 8:00 AM - 5:00 PM

### 💡 Consejos Rápidos
1. **Usar navegador actualizado** (Chrome 90+, Firefox 88+)
2. **Guardar token** para evitar re-autenticación constante
3. **Verificar permisos** antes de crear/editar recursos
4. **Revisar logs** ante cualquier problema
5. **Hacer backup** antes de cambios importantes

---

## 📝 FORMATO DE DATOS COMUNES

### 📅 Fechas
```
Formato: YYYY-MM-DD
Ejemplo: 2025-10-15
```

### ⏰ Horas
```
Formato: HH:MM
Ejemplo: 14:30
```

### 🚗 Placas de Vehículos
```
Formato: ABC123 o ABC12D
Ejemplos: XYZ789, DEF45G
```

### 📱 Teléfonos
```
Formato: 300-123-4567
Sin espacios: 3001234567
```

### 💰 Moneda
```
Formato: Número entero (pesos)
Ejemplo: 150000 (sin puntos ni comas)
```

---

**🎯 ¡Sistema listo para usar! Consulta la documentación completa en `/docs` para más detalles.**