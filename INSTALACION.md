# 🛠️ MANUAL DE INSTALACIÓN Y CONFIGURACIÓN
## Sistema de Gestión de Flota - Personería

---

## 📋 REQUISITOS DEL SISTEMA

### Hardware Mínimo
- **CPU**: 2 cores, 2.0 GHz o superior
- **RAM**: 4 GB (8 GB recomendado)
- **Almacenamiento**: 10 GB libres
- **Red**: Conexión a internet para alertas por email

### Software Requerido
- **Sistema Operativo**: Windows 10/11, Ubuntu 18+, macOS 10.15+
- **Python**: 3.8 o superior
- **Navegador**: Chrome 90+, Firefox 88+, Safari 14+

---

## ⬇️ DESCARGA E INSTALACIÓN

### Paso 1: Verificar Python
```powershell
# Verificar versión de Python
python --version

# Si no está instalado, descargar desde: https://python.org
# Asegurarse de marcar "Add Python to PATH"
```

### Paso 2: Descargar el Proyecto
```powershell
# El proyecto debe estar en:
C:\Users\[su_usuario]\formulario solicitudes\
```

### Paso 3: Navegar al Directorio del Backend
```powershell
cd "C:\Users\efren\formulario solicitudes\backend"
```

### Paso 4: Crear Entorno Virtual (Opcional pero Recomendado)
```powershell
# Crear entorno virtual
python -m venv fleet_env

# Activar entorno virtual
.\fleet_env\Scripts\Activate.ps1

# En caso de error de ejecución, ejecutar:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Paso 5: Instalar Dependencias
```powershell
# Opción 1: Instalación básica (recomendada para empezar)
pip install fastapi uvicorn sqlalchemy pydantic-settings
pip install python-multipart passlib python-jose bcrypt
pip install python-decouple email-validator python-dotenv APScheduler

# Opción 2: Desde requirements (si está disponible)
pip install -r requirements.txt

# Verificar instalación
pip list
```

---

## ⚙️ CONFIGURACIÓN INICIAL

### Crear Archivo de Configuración
```powershell
# Crear archivo .env en el directorio backend
notepad .env
```

### Configuración Básica (.env)
```env
# Base de datos (SQLite para desarrollo)
DATABASE_URL=sqlite:///./fleet_management.db

# Seguridad
SECRET_KEY=clave_super_secreta_de_64_caracteres_cambiar_en_produccion
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Configuración de la aplicación
DEBUG=True
ALLOWED_HOSTS=["*"]

# Email (opcional - para alertas)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=sistema@personeria.gov.co
EMAIL_PASSWORD=contraseña_de_aplicacion
FROM_EMAIL=sistema@personeria.gov.co

# Configuración de alertas
MAINTENANCE_KM_INTERVAL=10000
MAINTENANCE_ALERT_KM_THRESHOLD=1000
DOCUMENT_EXPIRY_WARNING_DAYS=30
DOCUMENT_CRITICAL_WARNING_DAYS=7

# Archivos
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=.xlsx,.xls,.csv,.pdf,.jpg,.png

# API
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

---

## 🗄️ INICIALIZAR BASE DE DATOS

### Ejecutar Script de Inicialización
```powershell
# Desde el directorio backend
python init_db.py
```

**Salida esperada:**
```
Base de datos inicializada correctamente
Usuario administrador creado:
  - Usuario: admin
  - Contraseña: admin123
¡Sistema listo para usar!
```

### Verificar Creación de la Base de Datos
```powershell
# Debe aparecer el archivo
dir fleet_management.db

# Salida esperada:
# fleet_management.db - [fecha] - [tamaño]KB
```

---

## 🚀 INICIAR EL SISTEMA

### Opción 1: Script Automático (Windows)
```powershell
# Ejecutar script de inicio
.\start.bat
```

### Opción 2: Comando Manual
```powershell
# Iniciar servidor de desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Opción 3: Con Configuraciones Específicas
```powershell
# Con workers múltiples (producción)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Solo acceso local
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Salida esperada del servidor:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## ✅ VERIFICACIÓN DE LA INSTALACIÓN

### Paso 1: Verificar Servidor Web
```powershell
# Abrir navegador web y ir a:
# http://localhost:8000

# O usando curl desde terminal:
curl http://localhost:8000/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "message": "Sistema de Gestión de Flota funcionando correctamente",
  "timestamp": "2025-10-01T10:30:00Z"
}
```

### Paso 2: Verificar Documentación API
```
URL: http://localhost:8000/docs
```
Debe mostrar la interfaz Swagger con todos los endpoints disponibles.

### Paso 3: Probar Autenticación
1. Ir a `/docs`
2. Buscar endpoint `POST /api/v1/auth/token`
3. Hacer clic en "Try it out"
4. Ingresar credenciales:
   - `username`: admin
   - `password`: admin123
5. Ejecutar y verificar que retorna un token

### Paso 4: Verificar Dashboard
```
GET http://localhost:8000/api/v1/dashboard/stats
```

---

## 📁 ESTRUCTURA DE DIRECTORIOS DESPUÉS DE LA INSTALACIÓN

```
backend/
├── fleet_management.db        # ✅ Base de datos SQLite
├── init_db.py                # Script de inicialización
├── start.bat                 # ✅ Script de inicio Windows
├── .env                      # ✅ Configuración (crear)
├── app/
│   ├── main.py              # ✅ Aplicación principal
│   ├── api/                 # Endpoints REST
│   ├── core/               # Configuración
│   ├── database/           # Modelos y BD
│   ├── schemas/           # Validaciones
│   └── services/          # Servicios
├── logs/                   # ✅ Directorio de logs (se crea automático)
├── uploads/               # ✅ Archivos subidos
│   ├── documents/
│   ├── excel/
│   └── images/
└── fleet_env/             # ✅ Entorno virtual (si se creó)
```

---

## 🔧 CONFIGURACIÓN AVANZADA

### Base de Datos PostgreSQL (Producción)
```env
# Instalar driver PostgreSQL
pip install psycopg2-binary

# Configurar en .env
DATABASE_URL=postgresql://usuario:contraseña@localhost/fleet_management
```

### Configuración de Email Gmail
1. **Habilitar verificación en 2 pasos** en Gmail
2. **Generar contraseña de aplicación**:
   - Ir a Cuenta de Google > Seguridad > Contraseñas de aplicaciones
   - Generar nueva contraseña para "Correo"
3. **Configurar en .env**:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=tu_email@gmail.com
EMAIL_PASSWORD=contraseña_de_aplicacion_generada
```

### Configuración SSL/HTTPS (Producción)
```powershell
# Instalar certificados SSL
pip install python-multipart[standard]

# Configurar servidor con SSL
uvicorn app.main:app --host 0.0.0.0 --port 443 --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

---

## 🚨 SOLUCIÓN DE PROBLEMAS COMUNES

### Error: "Python no se reconoce como comando"
**Solución:**
1. Reinstalar Python desde python.org
2. Marcar "Add Python to PATH" durante la instalación
3. Reiniciar PowerShell

### Error: "No module named 'fastapi'"
**Solución:**
```powershell
# Verificar pip
pip --version

# Reinstalar FastAPI
pip install --upgrade pip
pip install fastapi uvicorn
```

### Error: "Permission denied" en PowerShell
**Solución:**
```powershell
# Cambiar política de ejecución
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error: "Address already in use" (Puerto 8000 ocupado)
**Solución:**
```powershell
# Encontrar proceso usando puerto 8000
netstat -ano | findstr :8000

# Terminar proceso (usar PID del comando anterior)
taskkill /PID 1234 /F

# O usar puerto diferente
uvicorn app.main:app --port 8001
```

### Error: "Database locked"
**Solución:**
```powershell
# Terminar todos los procesos Python
taskkill /F /IM python.exe

# Reiniciar base de datos
python init_db.py
```

### Error de dependencias con pandas/numpy
**Solución:**
```powershell
# Si hay problemas con compilación, usar versión simplificada
pip install --only-binary=all pandas openpyxl

# O evitar estas dependencias por ahora (el sistema funciona sin ellas)
```

---

## 📊 VERIFICACIÓN DE RENDIMIENTO

### Prueba de Carga Básica
```powershell
# Instalar herramientas de testing
pip install requests

# Crear script de prueba simple
python test_simple.py
```

### Monitoreo de Recursos
```powershell
# Ver uso de CPU y memoria
tasklist | findstr python

# Ver conexiones de red
netstat -an | findstr :8000
```

---

## 🔄 COMANDOS DE MANTENIMIENTO

### Backup de Base de Datos
```powershell
# Crear backup manual
copy fleet_management.db backup\fleet_management_%date:~-4,4%%date:~-10,2%%date:~-7,2%.db
```

### Actualizar Sistema
```powershell
# Actualizar dependencias
pip install --upgrade fastapi uvicorn sqlalchemy

# Verificar integridad de BD
sqlite3 fleet_management.db "PRAGMA integrity_check;"
```

### Limpiar Logs
```powershell
# Limpiar logs antiguos (más de 30 días)
forfiles /p logs /s /m *.log /d -30 /c "cmd /c del @path"
```

---

## 📞 SOPORTE TÉCNICO

### Información del Sistema
```powershell
# Generar reporte del sistema
python -c "import sys, platform; print(f'Python: {sys.version}'); print(f'OS: {platform.platform()}')"
```

### Logs para Soporte
- **Ubicación de logs**: `backend/logs/app.log`
- **Configuración**: `backend/.env`
- **Estado de BD**: `backend/fleet_management.db`

### Contacto
- **Email**: soporte@personeria.gov.co
- **Teléfono**: (1) 123-456-7890
- **Horario**: Lunes a Viernes, 8:00 AM - 5:00 PM

---

## 🎯 SIGUIENTE PASO

Una vez completada la instalación exitosamente:

1. **Consultar la [Guía Rápida de Usuario](GUIA_RAPIDA.md)** para aprender a usar el sistema
2. **Revisar la [Documentación Técnica](DOCUMENTACION_TECNICA.md)** para configuraciones avanzadas
3. **Leer el [Manual Completo](MANUAL_COMPLETO.md)** para información detallada

**¡El Sistema de Gestión de Flota está listo para usar!** 🎉