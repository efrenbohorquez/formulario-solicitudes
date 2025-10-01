from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

Base = declarative_base()

class VehicleStatus(str, enum.Enum):
    DISPONIBLE = "disponible"
    EN_USO = "en_uso" 
    MANTENIMIENTO = "mantenimiento"
    FUERA_DE_SERVICIO = "fuera_de_servicio"

class VehicleType(str, enum.Enum):
    SEDAN = "sedan"
    SUV = "suv"
    CAMIONETA = "camioneta"
    BUS = "bus"

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    USUARIO = "usuario"
    MOTOCICLETA = "motocicleta"

class DriverStatus(str, enum.Enum):
    DISPONIBLE = "disponible"
    EN_SERVICIO = "en_servicio"
    DESCANSO = "descanso"
    INCAPACITADO = "incapacitado"

class MaintenanceType(str, enum.Enum):
    PREVENTIVO = "preventivo"
    CORRECTIVO = "correctivo"
    EMERGENCIA = "emergencia"
    REVISION_TECNICA = "revision_tecnica"

class MaintenanceStatus(str, enum.Enum):
    PROGRAMADO = "programado"
    EN_PROCESO = "en_proceso"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"

class RequestStatus(str, enum.Enum):
    PENDIENTE = "pendiente"
    ASIGNADO = "asignado"
    EN_CURSO = "en_curso"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"

class AlertPriority(str, enum.Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"

# Modelo de Vehículos
class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(10), unique=True, index=True, nullable=False)
    marca = Column(String(50), nullable=False)
    modelo = Column(String(50), nullable=False)
    año = Column(Integer, nullable=False)
    color = Column(String(30))
    tipo_vehiculo = Column(Enum(VehicleType), nullable=False)
    numero_motor = Column(String(50))
    numero_chasis = Column(String(50))
    cilindraje = Column(Integer)
    capacidad_pasajeros = Column(Integer)
    kilometraje = Column(Integer, default=0)
    estado = Column(Enum(VehicleStatus), default=VehicleStatus.DISPONIBLE)
    
    # Fechas importantes
    fecha_compra = Column(Date)
    fecha_soat = Column(Date)
    fecha_tecnicomecanica = Column(Date)
    fecha_seguro = Column(Date)
    
    # Información adicional
    observaciones = Column(Text)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    mantenimientos = relationship("Maintenance", back_populates="vehiculo")
    asignaciones = relationship("Assignment", back_populates="vehiculo")
    alertas = relationship("MaintenanceAlert", back_populates="vehiculo")

# Modelo de Conductores
class Driver(Base):
    __tablename__ = "drivers"
    
    id = Column(Integer, primary_key=True, index=True)
    cedula = Column(String(20), unique=True, index=True, nullable=False)
    nombre_completo = Column(String(100), nullable=False)
    telefono = Column(String(20))
    email = Column(String(100))
    direccion = Column(Text)
    
    # Información de licencia
    numero_licencia = Column(String(30), unique=True, nullable=False)
    categoria_licencia = Column(String(10), nullable=False)
    fecha_vencimiento_licencia = Column(Date, nullable=False)
    
    # Estado y disponibilidad
    estado = Column(Enum(DriverStatus), default=DriverStatus.DISPONIBLE)
    fecha_ingreso = Column(Date)
    años_experiencia = Column(Integer)
    
    # Información adicional
    observaciones = Column(Text)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    asignaciones = relationship("Assignment", back_populates="conductor")

# Modelo de Mantenimientos
class Maintenance(Base):
    __tablename__ = "maintenance"
    
    id = Column(Integer, primary_key=True, index=True)
    vehiculo_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    tipo_mantenimiento = Column(Enum(MaintenanceType), nullable=False)
    estado = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.PROGRAMADO)
    
    # Fechas
    fecha_programada = Column(DateTime, nullable=False)
    fecha_inicio = Column(DateTime)
    fecha_finalizacion = Column(DateTime)
    
    # Detalles del mantenimiento
    descripcion = Column(Text, nullable=False)
    kilometraje_actual = Column(Integer)
    costo_estimado = Column(Numeric(10, 2))
    costo_real = Column(Numeric(10, 2))
    
    # Proveedor/Taller
    taller_proveedor = Column(String(100))
    contacto_taller = Column(String(50))
    
    # Observaciones y detalles
    observaciones = Column(Text)
    repuestos_utilizados = Column(Text)
    proximo_mantenimiento_km = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    vehiculo = relationship("Vehicle", back_populates="mantenimientos")

# Modelo de Solicitudes de Transporte
class TransportRequest(Base):
    __tablename__ = "transport_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_solicitud = Column(String(50), unique=True, index=True)
    
    # Información del solicitante
    nombre_solicitante = Column(String(100), nullable=False)
    dependencia = Column(String(100))
    telefono_contacto = Column(String(20))
    email_contacto = Column(String(100))
    
    # Detalles del viaje
    fecha_solicitud = Column(DateTime, nullable=False)
    fecha_viaje = Column(DateTime, nullable=False)
    origen = Column(String(200), nullable=False)
    destino = Column(String(200), nullable=False)
    proposito_viaje = Column(Text)
    numero_pasajeros = Column(Integer, default=1)
    
    # Estado y asignación
    estado = Column(Enum(RequestStatus), default=RequestStatus.PENDIENTE)
    prioridad = Column(Enum(AlertPriority), default=AlertPriority.MEDIA)
    
    # Información adicional
    observaciones = Column(Text)
    requiere_vehiculo_especial = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    asignacion = relationship("Assignment", back_populates="solicitud", uselist=False)

# Modelo de Asignaciones
class Assignment(Base):
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    solicitud_id = Column(Integer, ForeignKey("transport_requests.id"), nullable=False)
    vehiculo_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    conductor_id = Column(Integer, ForeignKey("drivers.id"), nullable=False)
    
    # Detalles de la asignación
    fecha_asignacion = Column(DateTime, server_default=func.now())
    kilometraje_inicio = Column(Integer)
    kilometraje_fin = Column(Integer)
    
    # Estado del viaje
    fecha_inicio_real = Column(DateTime)
    fecha_fin_real = Column(DateTime)
    
    # Observaciones del viaje
    observaciones_conductor = Column(Text)
    calificacion_servicio = Column(Integer)  # 1-5
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    solicitud = relationship("TransportRequest", back_populates="asignacion")
    vehiculo = relationship("Vehicle", back_populates="asignaciones")
    conductor = relationship("Driver", back_populates="asignaciones")

# Modelo de Alertas de Mantenimiento
class MaintenanceAlert(Base):
    __tablename__ = "maintenance_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    vehiculo_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    
    tipo_alerta = Column(String(50), nullable=False)  # "kilometraje", "fecha_soat", "tecnicomecanica", etc.
    mensaje = Column(Text, nullable=False)
    prioridad = Column(Enum(AlertPriority), nullable=False)
    
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_vencimiento = Column(DateTime)
    activa = Column(Boolean, default=True)
    vista = Column(Boolean, default=False)
    
    # Relaciones
    vehiculo = relationship("Vehicle", back_populates="alertas")

# Modelo de Usuarios del Sistema
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    
    nombre_completo = Column(String(100))
    rol = Column(String(30), default="usuario")  # admin, gestor, conductor, usuario
    activo = Column(Boolean, default=True)
    
    # Configuraciones de notificación
    notificaciones_email = Column(Boolean, default=True)
    notificaciones_push = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime)