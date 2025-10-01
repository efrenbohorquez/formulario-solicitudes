#!/bin/bash
# Script de inicio rápido para el Sistema de Gestión de Flota

echo "🚀 Iniciando Sistema de Gestión de Flota"
echo "======================================="

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate  # Linux/Mac
# En Windows sería: venv\Scripts\activate

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo "⚙️ Creando archivo de configuración..."
    cp .env.example .env
    echo "✏️ IMPORTANTE: Edita el archivo .env con tu configuración"
fi

# Inicializar base de datos
echo "🗄️ Inicializando base de datos..."
python init_db.py

# Iniciar servidor
echo "🌐 Iniciando servidor en http://localhost:8000"
echo "📚 Documentación: http://localhost:8000/docs"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo "======================================="

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000