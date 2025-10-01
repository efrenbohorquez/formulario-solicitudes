from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

# Enums para esquemas
class VehicleStatus(str, Enum):
    DISPONIBLE = "disponible"
    EN_USO = "en_uso"
    MANTENIMIENTO = "mantenimiento"
    FUERA_DE_SERVICIO = "fuera_de_servicio"

class VehicleType(str, Enum):
    SEDAN = "sedan"
    SUV = "suv"
    CAMIONETA = "camioneta"
    BUS = "bus"
    MOTOCICLETA = "motocicleta"

class DriverStatus(str, Enum):
    DISPONIBLE = "disponible"
    EN_SERVICIO = "en_servicio"
    DESCANSO = "descanso"
    INCAPACITADO = "incapacitado"

class MaintenanceType(str, Enum):
    PREVENTIVO = "preventivo"
    CORRECTIVO = "correctivo"
    EMERGENCIA = "emergencia"
    REVISION_TECNICA = "revision_tecnica"

class MaintenanceStatus(str, Enum):
    PROGRAMADO = "programado"
    EN_PROCESO = "en_proceso"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"

class RequestStatus(str, Enum):
    PENDIENTE = "pendiente"
    ASIGNADO = "asignado"
    EN_CURSO = "en_curso"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"

class AlertPriority(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"

# Schemas para Vehículos
class VehicleBase(BaseModel):
    placa: str = Field(..., max_length=10, description="Placa del vehículo")
    marca: str = Field(..., max_length=50)
    modelo: str = Field(..., max_length=50)
    año: int = Field(..., ge=1900, le=2030)
    color: Optional[str] = Field(None, max_length=30)
    tipo_vehiculo: VehicleType
    numero_motor: Optional[str] = Field(None, max_length=50)
    numero_chasis: Optional[str] = Field(None, max_length=50)
    cilindraje: Optional[int] = Field(None, ge=0)
    capacidad_pasajeros: Optional[int] = Field(None, ge=1)
    kilometraje: Optional[int] = Field(0, ge=0)
    estado: Optional[VehicleStatus] = VehicleStatus.DISPONIBLE
    fecha_compra: Optional[date] = None
    fecha_soat: Optional[date] = None
    fecha_tecnicomecanica: Optional[date] = None
    fecha_seguro: Optional[date] = None
    observaciones: Optional[str] = None

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(BaseModel):
    placa: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    año: Optional[int] = None
    color: Optional[str] = None
    tipo_vehiculo: Optional[VehicleType] = None
    numero_motor: Optional[str] = None
    numero_chasis: Optional[str] = None
    cilindraje: Optional[int] = None
    capacidad_pasajeros: Optional[int] = None
    kilometraje: Optional[int] = None
    estado: Optional[VehicleStatus] = None
    fecha_compra: Optional[date] = None
    fecha_soat: Optional[date] = None
    fecha_tecnicomecanica: Optional[date] = None
    fecha_seguro: Optional[date] = None
    observaciones: Optional[str] = None

class Vehicle(VehicleBase):
    id: int
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas para Conductores
class DriverBase(BaseModel):
    cedula: str = Field(..., max_length=20)
    nombre_completo: str = Field(..., max_length=100)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None
    numero_licencia: str = Field(..., max_length=30)
    categoria_licencia: str = Field(..., max_length=10)
    fecha_vencimiento_licencia: date
    estado: Optional[DriverStatus] = DriverStatus.DISPONIBLE
    fecha_ingreso: Optional[date] = None
    años_experiencia: Optional[int] = Field(None, ge=0)
    observaciones: Optional[str] = None

class DriverCreate(DriverBase):
    pass

class DriverUpdate(BaseModel):
    cedula: Optional[str] = None
    nombre_completo: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None
    numero_licencia: Optional[str] = None
    categoria_licencia: Optional[str] = None
    fecha_vencimiento_licencia: Optional[date] = None
    estado: Optional[DriverStatus] = None
    fecha_ingreso: Optional[date] = None
    años_experiencia: Optional[int] = None
    observaciones: Optional[str] = None

class Driver(DriverBase):
    id: int
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas para Mantenimientos
class MaintenanceBase(BaseModel):
    vehiculo_id: int
    tipo_mantenimiento: MaintenanceType
    estado: Optional[MaintenanceStatus] = MaintenanceStatus.PROGRAMADO
    fecha_programada: datetime
    descripcion: str
    kilometraje_actual: Optional[int] = None
    costo_estimado: Optional[float] = None
    taller_proveedor: Optional[str] = None
    contacto_taller: Optional[str] = None
    observaciones: Optional[str] = None

class MaintenanceCreate(MaintenanceBase):
    pass

class MaintenanceUpdate(BaseModel):
    tipo_mantenimiento: Optional[MaintenanceType] = None
    estado: Optional[MaintenanceStatus] = None
    fecha_programada: Optional[datetime] = None
    fecha_inicio: Optional[datetime] = None
    fecha_finalizacion: Optional[datetime] = None
    descripcion: Optional[str] = None
    kilometraje_actual: Optional[int] = None
    costo_estimado: Optional[float] = None
    costo_real: Optional[float] = None
    taller_proveedor: Optional[str] = None
    contacto_taller: Optional[str] = None
    observaciones: Optional[str] = None
    repuestos_utilizados: Optional[str] = None
    proximo_mantenimiento_km: Optional[int] = None

class Maintenance(MaintenanceBase):
    id: int
    fecha_inicio: Optional[datetime] = None
    fecha_finalizacion: Optional[datetime] = None
    costo_real: Optional[float] = None
    repuestos_utilizados: Optional[str] = None
    proximo_mantenimiento_km: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas para Solicitudes
class TransportRequestBase(BaseModel):
    numero_solicitud: Optional[str] = None
    nombre_solicitante: str = Field(..., max_length=100)
    dependencia: Optional[str] = None
    telefono_contacto: Optional[str] = None
    email_contacto: Optional[EmailStr] = None
    fecha_viaje: datetime
    origen: str = Field(..., max_length=200)
    destino: str = Field(..., max_length=200)
    proposito_viaje: Optional[str] = None
    numero_pasajeros: Optional[int] = Field(1, ge=1)
    prioridad: Optional[AlertPriority] = AlertPriority.MEDIA
    observaciones: Optional[str] = None
    requiere_vehiculo_especial: Optional[bool] = False

class TransportRequestCreate(TransportRequestBase):
    pass

class TransportRequestUpdate(BaseModel):
    nombre_solicitante: Optional[str] = None
    dependencia: Optional[str] = None
    telefono_contacto: Optional[str] = None
    email_contacto: Optional[EmailStr] = None
    fecha_viaje: Optional[datetime] = None
    origen: Optional[str] = None
    destino: Optional[str] = None
    proposito_viaje: Optional[str] = None
    numero_pasajeros: Optional[int] = None
    estado: Optional[RequestStatus] = None
    prioridad: Optional[AlertPriority] = None
    observaciones: Optional[str] = None
    requiere_vehiculo_especial: Optional[bool] = None

class TransportRequest(TransportRequestBase):
    id: int
    estado: RequestStatus
    fecha_solicitud: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas para Asignaciones
class AssignmentBase(BaseModel):
    solicitud_id: int
    vehiculo_id: int
    conductor_id: int
    kilometraje_inicio: Optional[int] = None
    observaciones_conductor: Optional[str] = None

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentUpdate(BaseModel):
    vehiculo_id: Optional[int] = None
    conductor_id: Optional[int] = None
    kilometraje_inicio: Optional[int] = None
    kilometraje_fin: Optional[int] = None
    fecha_inicio_real: Optional[datetime] = None
    fecha_fin_real: Optional[datetime] = None
    observaciones_conductor: Optional[str] = None
    calificacion_servicio: Optional[int] = Field(None, ge=1, le=5)

class Assignment(AssignmentBase):
    id: int
    fecha_asignacion: datetime
    kilometraje_fin: Optional[int] = None
    fecha_inicio_real: Optional[datetime] = None
    fecha_fin_real: Optional[datetime] = None
    calificacion_servicio: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relaciones incluidas
    vehiculo: Optional[Vehicle] = None
    conductor: Optional[Driver] = None
    solicitud: Optional[TransportRequest] = None
    
    class Config:
        from_attributes = True

# Schemas para Alertas
class MaintenanceAlertBase(BaseModel):
    vehiculo_id: int
    tipo_alerta: str
    mensaje: str
    prioridad: AlertPriority
    fecha_vencimiento: Optional[datetime] = None

class MaintenanceAlertCreate(MaintenanceAlertBase):
    pass

class MaintenanceAlertUpdate(BaseModel):
    tipo_alerta: Optional[str] = None
    mensaje: Optional[str] = None
    prioridad: Optional[AlertPriority] = None
    fecha_vencimiento: Optional[datetime] = None
    activa: Optional[bool] = None
    vista: Optional[bool] = None

class MaintenanceAlert(MaintenanceAlertBase):
    id: int
    fecha_creacion: datetime
    activa: bool
    vista: bool
    vehiculo: Optional[Vehicle] = None
    
    class Config:
        from_attributes = True

# Schemas para Autenticación
class UserBase(BaseModel):
    username: str
    email: EmailStr
    nombre_completo: Optional[str] = None
    rol: Optional[str] = "usuario"

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nombre_completo: Optional[str] = None
    rol: Optional[str] = None
    activo: Optional[bool] = None
    notificaciones_email: Optional[bool] = None
    notificaciones_push: Optional[bool] = None

class User(UserBase):
    id: int
    activo: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: User

class TokenData(BaseModel):
    username: Optional[str] = None

# Schemas para Dashboard
class DashboardStats(BaseModel):
    total_vehiculos: int
    vehiculos_disponibles: int
    vehiculos_en_uso: int
    vehiculos_mantenimiento: int
    total_conductores: int
    conductores_disponibles: int
    solicitudes_pendientes: int
    alertas_activas: int
    mantenimientos_programados: int

class VehicleAvailability(BaseModel):
    id: int
    placa: str
    marca: str
    modelo: str
    estado: VehicleStatus
    kilometraje: int
    proxima_revision: Optional[date] = None

# Schemas para respuestas paginadas
class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    pages: int
    per_page: int