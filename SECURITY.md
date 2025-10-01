# Política de Seguridad

## 🔒 Reportes de Vulnerabilidades de Seguridad

La seguridad del Sistema de Gestión de Flota de Vehículos es una prioridad fundamental. Si descubres una vulnerabilidad de seguridad, por favor sigue el proceso establecido a continuación.

### ⚡ Vulnerabilidades Críticas (Reporte Inmediato)

Para vulnerabilidades que pueden ser explotadas inmediatamente y comprometen la seguridad del sistema:

1. **NO** abras un issue público
2. **NO** publiques detalles en discusiones públicas
3. Contacta directamente a los mantenedores:
   - Email: [pendiente configuración]
   - GitHub Security Advisories: [Reporte Privado](../../security/advisories/new)

### 🕐 Timeline de Respuesta

- **Acuse de recibo**: 24 horas
- **Evaluación inicial**: 72 horas
- **Plan de mitigación**: 1 semana
- **Parche de seguridad**: Según severidad (1-30 días)
- **Divulgación pública**: Después del parche y período de gracia

## 🛡️ Versiones Soportadas

Actualmente damos soporte de seguridad a las siguientes versiones:

| Versión | Soporte de Seguridad |
| ------- | -------------------- |
| 1.0.x   | ✅ Activo            |
| < 1.0   | ❌ No soportado      |

## 🎯 Alcance de Seguridad

### ✅ Dentro del Alcance

#### Vulnerabilidades del Backend (FastAPI)
- Inyección SQL
- Vulnerabilidades de autenticación/autorización
- Exposición de datos sensibles
- Vulnerabilidades de validación de entrada
- Ejecución remota de código (RCE)
- Escalación de privilegios
- Vulnerabilidades de sesión

#### Procesamiento de Archivos
- Carga de archivos maliciosos
- Vulnerabilidades en procesamiento Excel
- Directory traversal
- Inyección de comandos en procesamiento

#### Base de Datos
- Acceso no autorizado
- Filtración de datos
- Corrupción de datos por manipulación

#### Configuración y Despliegue
- Configuraciones inseguras por defecto
- Exposición de secretos/credenciales
- Vulnerabilidades en dependencias

### ❌ Fuera del Alcance

- Ataques de ingeniería social
- Phishing dirigido a usuarios
- Vulnerabilidades en servicios de terceros no integrados
- Ataques físicos a servidores
- Ataques DDoS (sin vulnerabilidad técnica específica)
- Problemas de usabilidad sin implicaciones de seguridad
- Vulnerabilidades que requieren acceso físico al servidor

## 🚨 Tipos de Vulnerabilidades Críticas

### Severidad Crítica (Parche en 1-7 días)
- Ejecución remota de código sin autenticación
- Escalación de privilegios a admin/root
- Acceso no autorizado a todos los datos
- Inyección SQL que permite lectura/escritura completa

### Severidad Alta (Parche en 7-14 días)
- Inyección SQL limitada
- Autenticación/autorización bypasseable
- Exposición masiva de datos sensibles
- Vulnerabilidades de validación críticas

### Severidad Media (Parche en 14-30 días)
- Cross-Site Scripting (XSS) persistente
- Exposición de información sensible limitada
- Vulnerabilidades de sesión
- CSRF en funciones críticas

### Severidad Baja (Parche en próxima release)
- Información disclosure menor
- Vulnerabilidades de configuración menores
- Issues de logging de seguridad

## 🔍 Proceso de Evaluación

### 1. Triaje Inicial
- Verificación de reproducibilidad
- Evaluación de impacto
- Clasificación de severidad
- Asignación de recursos

### 2. Análisis Detallado
- Análisis de código fuente
- Pruebas adicionales
- Evaluación de alcance
- Desarrollo de PoC interno

### 3. Desarrollo de Parche
- Diseño de solución
- Implementación y testing
- Revisión de código
- Testing de regresión

### 4. Despliegue y Comunicación
- Release de parche de seguridad
- Actualización de documentación
- Comunicación a usuarios
- Divulgación responsable

## 🛠️ Mejores Prácticas de Seguridad

### Para Desarrolladores

#### Validación de Entrada
```python
# ✅ Bueno: Validación estricta
from pydantic import BaseModel, validator

class VehiculoCreate(BaseModel):
    placa: str
    
    @validator('placa')
    def validate_placa(cls, v):
        if not re.match(r'^[A-Z]{3}-\d{3}$', v):
            raise ValueError('Formato de placa inválido')
        return v

# ❌ Malo: Sin validación
def crear_vehiculo(placa):
    # Directamente a la DB sin validar
    db.execute(f"INSERT INTO vehiculos (placa) VALUES ('{placa}')")
```

#### Autenticación Segura
```python
# ✅ Bueno: JWT con expiración
from datetime import datetime, timedelta
import jwt

def create_access_token(user_id: int):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"user_id": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# ❌ Malo: Token sin expiración
def create_token(user_id: int):
    return jwt.encode({"user_id": user_id}, SECRET_KEY)
```

#### Manejo Seguro de Archivos
```python
# ✅ Bueno: Validación de tipos y tamaños
ALLOWED_EXTENSIONS = {'.xlsx', '.xls'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_file(file):
    if file.size > MAX_FILE_SIZE:
        raise ValueError("Archivo demasiado grande")
    
    if not any(file.filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise ValueError("Tipo de archivo no permitido")

# ❌ Malo: Sin validación
def upload_file(file):
    # Guardar cualquier archivo sin verificar
    file.save(f"uploads/{file.filename}")
```

### Para Administradores

#### Configuración Segura
- Cambiar credenciales por defecto
- Usar HTTPS en producción
- Configurar firewalls apropiados
- Habilitar logging de seguridad
- Realizar backups regulares

#### Monitoreo
- Logs de autenticación fallida
- Patrones de acceso sospechosos
- Intentos de inyección SQL
- Cargas de archivos maliciosos

## 📊 Métricas de Seguridad

### Objetivos de Tiempo de Respuesta
- **Crítica**: < 24 horas para parche inicial
- **Alta**: < 72 horas para evaluación completa
- **Media**: < 1 semana para plan de mitigación
- **Baja**: < 1 mes para resolución

### Métricas de Calidad
- 100% de vulnerabilidades críticas parchadas en < 7 días
- 95% de vulnerabilidades altas parchadas en < 14 días
- 0 credenciales hardcodeadas en código fuente
- 100% de endpoints autenticados apropiadamente

## 🔐 Configuración de Seguridad Recomendada

### Variables de Entorno Críticas
```bash
# Autenticación
SECRET_KEY=tu_clave_secreta_muy_fuerte_de_al_menos_32_caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Base de Datos
DATABASE_URL=postgresql://usuario:password@localhost/fleet_db

# Archivo de logs
LOG_LEVEL=INFO
LOG_FILE=logs/security.log

# CORS (solo dominios confiables)
ALLOWED_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com
```

### Configuración de Producción
```python
# settings.py para producción
class ProductionSettings(BaseSettings):
    debug: bool = False
    testing: bool = False
    
    # Seguridad
    secret_key: str = Field(..., env="SECRET_KEY")
    allowed_hosts: list = ["yourdomain.com"]
    secure_cookies: bool = True
    
    # Base de datos
    database_url: str = Field(..., env="DATABASE_URL")
    
    # CORS
    cors_origins: list = Field(default_factory=list, env="ALLOWED_ORIGINS")
```

## 📞 Contacto y Recursos

### Contactos de Seguridad
- **Email de seguridad**: [Pendiente configuración]
- **GitHub Security**: Use GitHub Security Advisories
- **Emergencias**: [Número de contacto pendiente]

### Recursos Adicionales
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security Guide](https://fastapi.tiangolo.com/tutorial/security/)
- [Python Security Guide](https://python-security.readthedocs.io/)

### Herramientas Recomendadas
- **Static Analysis**: `bandit`, `safety`
- **Dependency Check**: `pip-audit`, `snyk`
- **Secrets Detection**: `trufflehog`, `detect-secrets`
- **Testing**: `pytest-security`

## 🏆 Programa de Reconocimiento

### Hall of Fame
Reconocemos públicamente a investigadores responsables que reportan vulnerabilidades:

*[Lista se actualizará conforme recibamos reportes válidos]*

### Criterios para Reconocimiento
- Reporte responsable siguiendo este proceso
- Vulnerabilidad válida dentro del alcance
- Cooperación durante el proceso de remediación
- No divulgación pública antes del parche

---

**Fecha de última actualización**: Enero 2025
**Versión de política**: 1.0

---
*Esta política está sujeta a cambios. Las actualizaciones se comunicarán a través de los canales oficiales del proyecto.*