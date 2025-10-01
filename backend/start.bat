@echo off
REM Script de inicio rápido para Windows - Sistema de Gestión de Flota

echo 🚀 Iniciando Sistema de Gestión de Flota
echo =======================================

REM Verificar si existe el entorno virtual
if not exist "venv" (
    echo 📦 Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
echo 🔧 Activando entorno virtual...
call venv\Scripts\activate

REM Instalar dependencias
echo 📚 Instalando dependencias...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Crear archivo .env si no existe
if not exist ".env" (
    echo ⚙️ Creando archivo de configuración...
    copy .env.example .env
    echo ✏️ IMPORTANTE: Edita el archivo .env con tu configuración
)

REM Inicializar base de datos
echo 🗄️ Inicializando base de datos...
python init_db.py

REM Iniciar servidor
echo 🌐 Iniciando servidor en http://localhost:8000
echo 📚 Documentación: http://localhost:8000/docs
echo.
echo Presiona Ctrl+C para detener el servidor
echo =======================================

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause