# 🔧 DOCUMENTACIÓN TÉCNICA AVANZADA
## Sistema de Gestión de Flota - Backend

---

## 📊 ARQUITECTURA DEL SISTEMA

### Diagrama de Arquitectura
```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND                             │
│   (React + TypeScript + Redux - En desarrollo)         │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP/REST API
┌─────────────────────▼───────────────────────────────────┐
│                   API LAYER                             │
│  FastAPI + Uvicorn (Puerto 8000)                      │
│  ├── Endpoints REST (/api/v1/*)                       │
│  ├── Documentación Swagger (/docs)                     │
│  ├── Autenticación JWT                                 │
│  └── Validación Pydantic                              │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                BUSINESS LAYER                           │
│  ├── Services (Lógica de Negocio)                     │
│  ├── Schemas (Validación de Datos)                     │
│  ├── Excel Processor (Importación)                     │
│  ├── Notification Service (Alertas)                    │
│  └── Scheduler (Tareas Automáticas)                    │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                  DATA LAYER                             │
│  SQLAlchemy ORM + SQLite                               │
│  ├── Models (Entidades)                                │
│  ├── Database Session Management                       │
│  ├── Migrations (Futuro con Alembic)                   │
│  └── Backup/Recovery                                   │
└─────────────────────────────────────────────────────────┘
```

### Tecnologías Core

| Componente | Tecnología | Versión | Propósito |
|------------|------------|---------|-----------|
| **Web Framework** | FastAPI | 0.104+ | API REST principal |
| **ASGI Server** | Uvicorn | 0.24+ | Servidor de aplicación |
| **ORM** | SQLAlchemy | 2.0+ | Mapeo objeto-relacional |
| **Base de Datos** | SQLite | 3.36+ | Almacenamiento (desarrollo) |
| **Validación** | Pydantic | 2.0+ | Schemas y validación |
| **Autenticación** | PyJWT + Passlib | - | JWT + Hash de contraseñas |
| **Scheduler** | APScheduler | 3.10+ | Tareas programadas |

---

## 🗄️ DISEÑO DE BASE DE DATOS

### Modelo Entidad-Relación
```sql
┌─────────────────┐     ┌─────────────────┐
│     USERS       │────▶│    VEHICLES     │
│  ├─ id (PK)     │     │  ├─ id (PK)     │
│  ├─ username    │     │  ├─ placa       │
│  ├─ email       │     │  ├─ marca       │
│  ├─ password    │     │  ├─ modelo      │
│  ├─ rol         │     │  ├─ estado      │
│  └─ created_at  │     │  └─ kilometraje │
└─────────────────┘     └─────────────────┘
         │                       │
         │                       │
┌─────────▼────────┐     ┌─────────▼────────┐
│     DRIVERS      │     │   MAINTENANCES   │
│  ├─ id (PK)      │     │  ├─ id (PK)      │
│  ├─ cedula       │     │  ├─ vehicle_id   │
│  ├─ nombre       │     │  ├─ tipo         │
│  ├─ telefono     │     │  ├─ fecha_prog   │
│  ├─ licencia_num │     │  ├─ costo        │
│  └─ estado       │     │  └─ descripcion  │
└──────────────────┘     └──────────────────┘
         │                       
         │                
┌─────────▼────────┐     ┌─────────────────┐
│ TRANSPORT_REQUESTS│     │   ASSIGNMENTS   │
│  ├─ id (PK)      │────▶│  ├─ id (PK)     │
│  ├─ solicitante  │     │  ├─ request_id  │
│  ├─ fecha_viaje  │     │  ├─ vehicle_id  │
│  ├─ origen       │     │  ├─ driver_id   │
│  ├─ destino      │     │  ├─ estado      │
│  └─ estado       │     │  └─ created_at  │
└──────────────────┘     └─────────────────┘
```

### Scripts SQL de Creación

#### Tabla Vehicles
```sql
CREATE TABLE vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placa VARCHAR(10) UNIQUE NOT NULL,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    año INTEGER,
    tipo_vehiculo VARCHAR(20) NOT NULL DEFAULT 'sedan',
    color VARCHAR(30),
    numero_motor VARCHAR(50),
    estado VARCHAR(20) NOT NULL DEFAULT 'disponible',
    kilometraje INTEGER DEFAULT 0,
    combustible VARCHAR(20) DEFAULT 'gasolina',
    soat_vencimiento DATE,
    tecnomecanica_vencimiento DATE,
    tarjeta_propiedad VARCHAR(50),
    poliza_numero VARCHAR(50),
    poliza_vencimiento DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabla Drivers
```sql
CREATE TABLE drivers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cedula VARCHAR(20) UNIQUE NOT NULL,
    nombre_completo VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    licencia_numero VARCHAR(30),
    licencia_categoria VARCHAR(10),
    licencia_vencimiento DATE,
    años_experiencia INTEGER DEFAULT 0,
    estado VARCHAR(20) NOT NULL DEFAULT 'disponible',
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Índices para Optimización
```sql
-- Índices de rendimiento
CREATE INDEX idx_vehicles_placa ON vehicles(placa);
CREATE INDEX idx_vehicles_estado ON vehicles(estado);
CREATE INDEX idx_drivers_cedula ON drivers(cedula);
CREATE INDEX idx_drivers_estado ON drivers(estado);
CREATE INDEX idx_maintenances_vehicle ON maintenances(vehicle_id);
CREATE INDEX idx_maintenances_fecha ON maintenances(fecha_programada);
CREATE INDEX idx_assignments_vehicle ON assignments(vehicle_id);
CREATE INDEX idx_assignments_driver ON assignments(driver_id);
```

---

## 🎯 ESTRUCTURA DE CÓDIGO

### Organización de Directorios
```
backend/
├── app/                        # Aplicación principal
│   ├── __init__.py            # Inicialización
│   ├── main.py                # Punto de entrada FastAPI
│   ├── api/                   # Capa de API
│   │   └── v1/               # Versión 1 de la API
│   │       ├── api.py        # Router principal
│   │       └── endpoints/    # Endpoints específicos
│   │           ├── auth.py
│   │           ├── vehicles.py
│   │           ├── drivers.py
│   │           ├── maintenance.py
│   │           ├── requests.py
│   │           ├── assignments.py
│   │           ├── alerts.py
│   │           └── dashboard.py
│   ├── core/                  # Configuración central
│   │   ├── config.py         # Variables de configuración
│   │   └── database.py       # Conexión a BD
│   ├── database/             # Capa de datos
│   │   ├── models.py         # Modelos SQLAlchemy
│   │   └── database.py       # Configuración BD
│   ├── schemas/              # Validación Pydantic
│   │   └── schemas.py        # DTOs de entrada/salida
│   └── services/             # Lógica de negocio
│       ├── excel_processor.py
│       ├── notification_service.py
│       └── scheduler.py
├── logs/                      # Archivos de log
├── uploads/                   # Archivos subidos
│   ├── documents/
│   ├── excel/
│   └── images/
├── init_db.py                # Script inicialización BD
├── requirements.txt          # Dependencias Python
├── start.bat                 # Script inicio Windows
└── .env                      # Variables de entorno
```

### Patrones de Diseño Implementados

#### 1. Repository Pattern
```python
# app/database/models.py
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(10), unique=True, index=True, nullable=False)
    marca = Column(String(50), nullable=False)
    modelo = Column(String(50), nullable=False)
    estado = Column(String(20), default="disponible")
    
    def to_dict(self):
        """Convierte el modelo a diccionario para serialización"""
        return {column.name: getattr(self, column.name) 
                for column in self.__table__.columns}
```

#### 2. DTO/Schema Pattern
```python
# app/schemas/schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class VehicleEstado(str, Enum):
    DISPONIBLE = "disponible"
    EN_USO = "en_uso"
    MANTENIMIENTO = "mantenimiento"
    FUERA_SERVICIO = "fuera_servicio"

class VehicleBase(BaseModel):
    placa: str = Field(..., min_length=6, max_length=10)
    marca: str = Field(..., min_length=1, max_length=50)
    modelo: str = Field(..., min_length=1, max_length=50)
    año: Optional[int] = Field(None, ge=1990, le=2030)

class VehicleCreate(VehicleBase):
    """Schema para crear vehículo"""
    pass

class VehicleResponse(VehicleBase):
    """Schema para respuesta de vehículo"""
    id: int
    estado: VehicleEstado
    kilometraje: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

#### 3. Service Layer Pattern
```python
# app/services/vehicle_service.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.models import Vehicle
from app.schemas.schemas import VehicleCreate, VehicleUpdate

class VehicleService:
    """Servicio para lógica de negocio de vehículos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_vehicle(self, vehicle: VehicleCreate) -> Vehicle:
        """Crear nuevo vehículo con validaciones de negocio"""
        # Verificar placa única
        existing = self.db.query(Vehicle).filter(
            Vehicle.placa == vehicle.placa
        ).first()
        
        if existing:
            raise ValueError(f"Ya existe un vehículo con placa {vehicle.placa}")
        
        # Crear vehículo
        db_vehicle = Vehicle(**vehicle.dict())
        self.db.add(db_vehicle)
        self.db.commit()
        self.db.refresh(db_vehicle)
        
        return db_vehicle
    
    def get_available_vehicles(self) -> List[Vehicle]:
        """Obtener vehículos disponibles para asignación"""
        return self.db.query(Vehicle).filter(
            Vehicle.estado == "disponible"
        ).all()
    
    def calculate_maintenance_due(self, vehicle: Vehicle) -> bool:
        """Calcular si el vehículo necesita mantenimiento"""
        # Lógica de negocio para mantenimiento
        maintenance_interval = 10000  # km
        last_maintenance_km = vehicle.kilometraje_ultimo_mantenimiento or 0
        current_km = vehicle.kilometraje
        
        return (current_km - last_maintenance_km) >= maintenance_interval
```

---

## 🔌 ENDPOINTS DE API

### Documentación OpenAPI

#### Swagger UI
- **URL**: http://localhost:8000/docs
- **Descripción**: Interfaz interactiva para probar endpoints
- **Autenticación**: Token Bearer JWT

#### Redoc
- **URL**: http://localhost:8000/redoc
- **Descripción**: Documentación alternativa más limpia

### Endpoints Implementados

#### Autenticación
```python
POST   /api/v1/auth/token      # Obtener token JWT
POST   /api/v1/auth/register   # Registrar usuario
GET    /api/v1/auth/me        # Perfil usuario actual
```

#### Vehículos
```python
GET    /api/v1/vehicles                    # Listar vehículos
POST   /api/v1/vehicles                    # Crear vehículo
GET    /api/v1/vehicles/{id}               # Obtener vehículo
PUT    /api/v1/vehicles/{id}               # Actualizar vehículo
DELETE /api/v1/vehicles/{id}               # Eliminar vehículo
GET    /api/v1/vehicles/available          # Vehículos disponibles
PUT    /api/v1/vehicles/{id}/estado        # Cambiar estado
```

#### Conductores
```python
GET    /api/v1/drivers                     # Listar conductores
POST   /api/v1/drivers                     # Crear conductor
GET    /api/v1/drivers/{id}                # Obtener conductor
PUT    /api/v1/drivers/{id}                # Actualizar conductor
DELETE /api/v1/drivers/{id}                # Eliminar conductor
GET    /api/v1/drivers/available           # Conductores disponibles
```

#### Mantenimientos
```python
GET    /api/v1/maintenance                 # Listar mantenimientos
POST   /api/v1/maintenance                 # Programar mantenimiento
GET    /api/v1/maintenance/{id}            # Obtener mantenimiento
PUT    /api/v1/maintenance/{id}            # Actualizar mantenimiento
GET    /api/v1/maintenance/due             # Mantenimientos vencidos
```

#### Solicitudes y Asignaciones
```python
GET    /api/v1/requests                    # Listar solicitudes
POST   /api/v1/requests                    # Crear solicitud
POST   /api/v1/requests/import-excel       # Importar desde Excel
GET    /api/v1/assignments                 # Listar asignaciones
POST   /api/v1/assignments                 # Crear asignación
PUT    /api/v1/assignments/{id}/complete   # Completar viaje
```

#### Dashboard y Alertas
```python
GET    /api/v1/dashboard/stats             # Estadísticas generales
GET    /api/v1/dashboard/kpis              # Indicadores clave
GET    /api/v1/alerts                      # Alertas activas
GET    /api/v1/alerts/critical             # Alertas críticas
```

### Formato de Respuesta Estándar

#### Respuesta Exitosa
```json
{
  "success": true,
  "data": {
    "id": 1,
    "placa": "ABC123",
    "marca": "Toyota",
    "modelo": "Corolla"
  },
  "message": "Vehículo creado exitosamente",
  "timestamp": "2025-10-01T10:30:00Z"
}
```

#### Respuesta de Error
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Los datos proporcionados no son válidos",
    "details": {
      "placa": ["Este campo es obligatorio"],
      "año": ["Debe ser un año válido entre 1990 y 2030"]
    }
  },
  "timestamp": "2025-10-01T10:30:00Z"
}
```

#### Paginación
```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 45,
    "page": 1,
    "pages": 3,
    "limit": 20,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## 🔒 SEGURIDAD

### Autenticación JWT

#### Configuración
```python
# app/core/config.py
SECRET_KEY = "clave_super_secreta_de_64_caracteres"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 horas

# Generación de token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

#### Middleware de Autenticación
```python
# app/api/dependencies.py
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Buscar usuario en BD
    user = get_user_by_username(username)
    if user is None:
        raise credentials_exception
    
    return user
```

### Control de Acceso por Roles

#### Definición de Roles
```python
# app/database/models.py
class UserRole(str, Enum):
    ADMIN = "admin"           # Acceso total
    SUPERVISOR = "supervisor" # Gestión operativa
    USUARIO = "usuario"       # Solo consultas

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    rol = Column(Enum(UserRole), default=UserRole.USUARIO)
```

#### Decorador de Permisos
```python
# app/core/permissions.py
from functools import wraps
from fastapi import HTTPException, status

def require_role(allowed_roles: List[UserRole]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if current_user.rol not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tiene permisos para realizar esta acción"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Uso en endpoints
@router.post("/vehicles")
@require_role([UserRole.ADMIN, UserRole.SUPERVISOR])
async def create_vehicle(vehicle: VehicleCreate):
    pass
```

### Validación de Datos

#### Sanitización de Entradas
```python
# app/schemas/schemas.py
from pydantic import validator, Field
import re

class VehicleCreate(BaseModel):
    placa: str = Field(..., min_length=6, max_length=10)
    
    @validator('placa')
    def validate_placa(cls, v):
        # Remover espacios y convertir a mayúsculas
        v = v.strip().upper()
        
        # Validar formato colombiano (ABC123 o ABC12D)
        pattern = r'^[A-Z]{3}[0-9]{2}[0-9A-Z]?$'
        if not re.match(pattern, v):
            raise ValueError('Formato de placa inválido')
        
        return v
    
    @validator('año')
    def validate_año(cls, v):
        if v is not None:
            current_year = datetime.now().year
            if v < 1990 or v > current_year + 1:
                raise ValueError('Año debe estar entre 1990 y {}'.format(current_year + 1))
        return v
```

---

## 📊 LOGGING Y MONITOREO

### Configuración de Logging
```python
# app/core/logging.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    # Crear directorio de logs
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Configurar formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para archivo con rotación
    file_handler = RotatingFileHandler(
        f'{log_dir}/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configurar logger principal
    logger = logging.getLogger("fleet_management")
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Uso en la aplicación
logger = setup_logging()
logger.info("Sistema iniciado correctamente")
```

### Eventos de Auditoría
```python
# app/services/audit_service.py
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Text

class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    ASSIGN = "assign"

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    action = Column(String(20), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(20))
    description = Column(Text)
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow)

def log_audit_event(user_id: int, action: AuditAction, 
                   entity_type: str, entity_id: str = None, 
                   description: str = None, ip_address: str = None):
    """Registrar evento de auditoría"""
    audit_entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        ip_address=ip_address
    )
    
    db.add(audit_entry)
    db.commit()
    
    logger.info(f"Audit: User {user_id} {action} {entity_type} {entity_id}")
```

---

## ⚙️ TAREAS AUTOMÁTICAS

### Configuración del Scheduler
```python
# app/services/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import atexit

class TaskScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.setup_jobs()
        
    def setup_jobs(self):
        """Configurar tareas programadas"""
        
        # Verificar vencimientos diariamente a las 8:00 AM
        self.scheduler.add_job(
            func=self.check_expirations,
            trigger=CronTrigger(hour=8, minute=0),
            id='check_expirations',
            name='Verificar vencimientos de documentos'
        )
        
        # Alertas de mantenimiento cada 6 horas
        self.scheduler.add_job(
            func=self.check_maintenance_due,
            trigger=IntervalTrigger(hours=6),
            id='check_maintenance',
            name='Verificar mantenimientos programados'
        )
        
        # Limpiar logs antiguos semanalmente
        self.scheduler.add_job(
            func=self.cleanup_old_logs,
            trigger=CronTrigger(day_of_week='sun', hour=2, minute=0),
            id='cleanup_logs',
            name='Limpiar logs antiguos'
        )
        
    def start(self):
        """Iniciar scheduler"""
        self.scheduler.start()
        logger.info("Scheduler iniciado correctamente")
        
        # Registrar limpieza al cerrar aplicación
        atexit.register(lambda: self.scheduler.shutdown())
    
    def check_expirations(self):
        """Verificar documentos próximos a vencer"""
        logger.info("Ejecutando verificación de vencimientos...")
        
        # Verificar SOAT
        vehicles_soat_expiring = db.query(Vehicle).filter(
            Vehicle.soat_vencimiento <= datetime.now() + timedelta(days=30),
            Vehicle.soat_vencimiento > datetime.now()
        ).all()
        
        for vehicle in vehicles_soat_expiring:
            send_alert(
                type="document_expiry",
                message=f"SOAT del vehículo {vehicle.placa} vence el {vehicle.soat_vencimiento}",
                priority="high" if (vehicle.soat_vencimiento - datetime.now().date()).days <= 7 else "medium"
            )
    
    def check_maintenance_due(self):
        """Verificar mantenimientos programados"""
        logger.info("Verificando mantenimientos programados...")
        
        # Lógica de verificación de mantenimiento por kilometraje
        for vehicle in db.query(Vehicle).all():
            if self.is_maintenance_due(vehicle):
                send_alert(
                    type="maintenance_due",
                    message=f"Vehículo {vehicle.placa} requiere mantenimiento",
                    priority="medium"
                )
```

### Notificaciones por Email
```python
# app/services/notification_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

class NotificationService:
    def __init__(self):
        self.smtp_server = settings.EMAIL_HOST
        self.smtp_port = settings.EMAIL_PORT
        self.email_user = settings.EMAIL_USER
        self.email_password = settings.EMAIL_PASSWORD
    
    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False):
        """Enviar email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html' if is_html else 'plain', 'utf-8'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            
            text = msg.as_string()
            server.sendmail(self.email_user, to_email, text)
            server.quit()
            
            logger.info(f"Email enviado correctamente a {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email a {to_email}: {str(e)}")
            return False
    
    def send_maintenance_alert(self, vehicle: Vehicle, maintenance_type: str):
        """Enviar alerta de mantenimiento"""
        subject = f"⚠️ Alerta de Mantenimiento - {vehicle.placa}"
        
        body = f"""
        <h2>Alerta de Mantenimiento</h2>
        <p><strong>Vehículo:</strong> {vehicle.marca} {vehicle.modelo}</p>
        <p><strong>Placa:</strong> {vehicle.placa}</p>
        <p><strong>Tipo:</strong> {maintenance_type}</p>
        <p><strong>Kilometraje actual:</strong> {vehicle.kilometraje:,} km</p>
        <p><strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        
        <p>Por favor, programe el mantenimiento correspondiente.</p>
        """
        
        # Enviar a supervisores
        supervisors = db.query(User).filter(
            User.rol.in_([UserRole.ADMIN, UserRole.SUPERVISOR])
        ).all()
        
        for supervisor in supervisors:
            if supervisor.email:
                self.send_email(supervisor.email, subject, body, is_html=True)
```

---

## 🧪 TESTING

### Configuración de Tests
```python
# test_system.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.database import get_db
from app.database.models import Base

# Base de datos de prueba en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_headers(client):
    # Crear usuario de prueba y obtener token
    response = client.post("/api/v1/auth/token", data={
        "username": "admin",
        "password": "admin123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### Tests Unitarios
```python
def test_create_vehicle(client, auth_headers):
    """Test crear vehículo"""
    vehicle_data = {
        "placa": "TEST123",
        "marca": "Toyota",
        "modelo": "Corolla",
        "año": 2020,
        "tipo_vehiculo": "sedan",
        "color": "Blanco"
    }
    
    response = client.post(
        "/api/v1/vehicles",
        json=vehicle_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["placa"] == "TEST123"
    assert data["estado"] == "disponible"

def test_duplicate_placa_error(client, auth_headers):
    """Test error por placa duplicada"""
    vehicle_data = {
        "placa": "DUP123",
        "marca": "Toyota",
        "modelo": "Corolla"
    }
    
    # Crear primer vehículo
    client.post("/api/v1/vehicles", json=vehicle_data, headers=auth_headers)
    
    # Intentar crear duplicado
    response = client.post("/api/v1/vehicles", json=vehicle_data, headers=auth_headers)
    
    assert response.status_code == 400
    assert "ya existe" in response.json()["detail"]
```

### Tests de Integración
```python
def test_full_workflow_request_assignment(client, auth_headers):
    """Test completo: solicitud → asignación → viaje"""
    
    # 1. Crear vehículo
    vehicle_response = client.post("/api/v1/vehicles", json={
        "placa": "WF123",
        "marca": "Toyota",
        "modelo": "Corolla"
    }, headers=auth_headers)
    vehicle_id = vehicle_response.json()["id"]
    
    # 2. Crear conductor
    driver_response = client.post("/api/v1/drivers", json={
        "cedula": "12345678",
        "nombre_completo": "Juan Pérez",
        "licencia_numero": "987654321"
    }, headers=auth_headers)
    driver_id = driver_response.json()["id"]
    
    # 3. Crear solicitud
    request_response = client.post("/api/v1/requests", json={
        "solicitante_nombre": "María García",
        "dependencia": "Jurídica",
        "fecha_viaje": "2025-10-15",
        "origen": "Sede",
        "destino": "Juzgado"
    }, headers=auth_headers)
    request_id = request_response.json()["id"]
    
    # 4. Crear asignación
    assignment_response = client.post("/api/v1/assignments", json={
        "request_id": request_id,
        "vehicle_id": vehicle_id,
        "driver_id": driver_id
    }, headers=auth_headers)
    
    assert assignment_response.status_code == 201
    
    # 5. Verificar estados
    vehicle_check = client.get(f"/api/v1/vehicles/{vehicle_id}", headers=auth_headers)
    assert vehicle_check.json()["estado"] == "en_uso"
    
    driver_check = client.get(f"/api/v1/drivers/{driver_id}", headers=auth_headers)
    assert driver_check.json()["estado"] == "en_servicio"
```

---

## 🚀 DEPLOYMENT

### Configuración de Producción

#### Variables de Entorno de Producción
```env
# .env.production
DATABASE_URL=postgresql://fleet_user:secure_password@localhost/fleet_management_prod
SECRET_KEY=clave_super_secreta_de_produccion_de_64_caracteres_minimo
DEBUG=False
ALLOWED_HOSTS=["tu-dominio.com", "www.tu-dominio.com"]

# Email de producción
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=sistema@personeria.gov.co
EMAIL_PASSWORD=contraseña_de_aplicacion_gmail

# Configuración de logs
LOG_LEVEL=INFO
LOG_FILE=/var/log/fleet_management/app.log

# Límites de archivos
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=.xlsx,.xls,.pdf,.jpg,.png
```

#### Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY ./app ./app
COPY init_db.py .

# Crear directorios necesarios
RUN mkdir -p logs uploads/documents uploads/excel uploads/images

# Variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://fleet_user:fleet_pass@db:5432/fleet_db
    depends_on:
      - db
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs

  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=fleet_user
      - POSTGRES_PASSWORD=fleet_pass
      - POSTGRES_DB=fleet_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app

volumes:
  postgres_data:
```

### Optimizaciones de Rendimiento

#### Configuración de Uvicorn para Producción
```bash
# Comando optimizado para producción
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --access-log \
  --log-level info
```

#### Nginx Reverse Proxy
```nginx
# nginx.conf
server {
    listen 80;
    server_name tu-dominio.com;

    # Redireccionar a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # Configuración de seguridad SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    # Configuración de proxy
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Servir archivos estáticos
    location /uploads/ {
        alias /app/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Limitar tamaño de archivos
    client_max_body_size 10M;
}
```

---

## 🔍 TROUBLESHOOTING AVANZADO

### Herramientas de Diagnóstico
```python
# app/core/diagnostics.py
import psutil
import sqlite3
from datetime import datetime
from typing import Dict, Any

class SystemDiagnostics:
    """Herramientas de diagnóstico del sistema"""
    
    def get_system_info(self) -> Dict[str, Any]:
        """Información del sistema"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def check_database_health(self) -> Dict[str, Any]:
        """Verificar salud de la base de datos"""
        try:
            conn = sqlite3.connect('fleet_management.db')
            cursor = conn.cursor()
            
            # Verificar integridad
            cursor.execute("PRAGMA integrity_check;")
            integrity = cursor.fetchone()[0]
            
            # Contar registros por tabla
            tables = ['vehicles', 'drivers', 'users', 'maintenances', 'transport_requests']
            counts = {}
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]
            
            # Tamaño de la base de datos
            cursor.execute("PRAGMA page_count;")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size;")
            page_size = cursor.fetchone()[0]
            db_size = page_count * page_size
            
            conn.close()
            
            return {
                "integrity": integrity,
                "table_counts": counts,
                "database_size": db_size,
                "status": "healthy" if integrity == "ok" else "corrupted"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def check_api_endpoints(self) -> Dict[str, str]:
        """Verificar endpoints de la API"""
        import requests
        
        endpoints = [
            "/health",
            "/docs",
            "/api/v1/vehicles",
            "/api/v1/dashboard/stats"
        ]
        
        results = {}
        base_url = "http://localhost:8000"
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                results[endpoint] = f"{response.status_code} - {response.reason}"
            except Exception as e:
                results[endpoint] = f"Error: {str(e)}"
        
        return results
```

### Script de Mantenimiento Automático
```python
# maintenance_script.py
#!/usr/bin/env python3
"""
Script de mantenimiento automático del sistema
Ejecutar semanalmente o cuando haya problemas de rendimiento
"""

import os
import sqlite3
import shutil
from datetime import datetime, timedelta
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('maintenance.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def backup_database():
    """Crear backup de la base de datos"""
    logger = setup_logging()
    
    try:
        source = 'fleet_management.db'
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'{backup_dir}/fleet_management_{timestamp}.db'
        
        shutil.copy2(source, backup_file)
        logger.info(f"Backup creado: {backup_file}")
        
        # Limpiar backups antiguos (mantener últimos 10)
        cleanup_old_backups(backup_dir)
        
    except Exception as e:
        logger.error(f"Error creando backup: {e}")

def cleanup_old_backups(backup_dir, keep_count=10):
    """Limpiar backups antiguos"""
    logger = setup_logging()
    
    try:
        backups = [f for f in os.listdir(backup_dir) if f.startswith('fleet_management_')]
        backups.sort(reverse=True)  # Más recientes primero
        
        for backup in backups[keep_count:]:
            os.remove(os.path.join(backup_dir, backup))
            logger.info(f"Backup eliminado: {backup}")
            
    except Exception as e:
        logger.error(f"Error limpiando backups: {e}")

def optimize_database():
    """Optimizar base de datos"""
    logger = setup_logging()
    
    try:
        conn = sqlite3.connect('fleet_management.db')
        cursor = conn.cursor()
        
        # Vacuum para compactar BD
        logger.info("Ejecutando VACUUM...")
        cursor.execute("VACUUM;")
        
        # Reindexar
        logger.info("Reindexando...")
        cursor.execute("REINDEX;")
        
        # Analizar estadísticas
        logger.info("Analizando estadísticas...")
        cursor.execute("ANALYZE;")
        
        conn.commit()
        conn.close()
        
        logger.info("Optimización completada")
        
    except Exception as e:
        logger.error(f"Error optimizando BD: {e}")

def cleanup_logs():
    """Limpiar logs antiguos"""
    logger = setup_logging()
    
    try:
        log_dir = 'logs'
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for filename in os.listdir(log_dir):
            filepath = os.path.join(log_dir, filename)
            
            if os.path.isfile(filepath):
                file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                
                if file_time < cutoff_date:
                    os.remove(filepath)
                    logger.info(f"Log eliminado: {filename}")
                    
    except Exception as e:
        logger.error(f"Error limpiando logs: {e}")

def main():
    """Ejecutar todas las tareas de mantenimiento"""
    logger = setup_logging()
    logger.info("=== Iniciando mantenimiento automático ===")
    
    backup_database()
    optimize_database()
    cleanup_logs()
    
    logger.info("=== Mantenimiento completado ===")

if __name__ == "__main__":
    main()
```

---

**© 2025 Sistema de Gestión de Flota - Documentación Técnica v1.0.0**