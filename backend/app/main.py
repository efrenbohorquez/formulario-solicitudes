from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configurar logging simple
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear instancia de FastAPI simple
app = FastAPI(
    title="Sistema de Gestión de Flota - Personería",
    description="API para gestión completa de vehículos, conductores y mantenimientos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS básico
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints básicos
@app.get("/")
def root():
    """Endpoint raíz"""
    return {
        "message": "Sistema de Gestión de Flota - Personería",
        "version": "1.0.0", 
        "status": "active",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/api/v1/test")
def test_endpoint():
    """Endpoint de prueba"""
    return {
        "message": "API funcionando correctamente",
        "timestamp": "2025-10-01"
    }

# Endpoints básicos para vehículos (simulados)
@app.get("/api/v1/vehicles")
def get_vehicles():
    """Lista de vehículos (datos simulados)"""
    return {
        "vehicles": [
            {
                "id": 1,
                "placa": "ABC123",
                "marca": "Toyota",
                "modelo": "Corolla",
                "estado": "disponible"
            },
            {
                "id": 2,
                "placa": "XYZ789",
                "marca": "Chevrolet", 
                "modelo": "Spark",
                "estado": "en_uso"
            }
        ],
        "total": 2
    }

@app.get("/api/v1/drivers")
def get_drivers():
    """Lista de conductores (datos simulados)"""
    return {
        "drivers": [
            {
                "id": 1,
                "nombre": "Juan Pérez",
                "cedula": "12345678",
                "estado": "disponible"
            },
            {
                "id": 2,
                "nombre": "María García",
                "cedula": "87654321", 
                "estado": "en_servicio"
            }
        ],
        "total": 2
    }

@app.get("/api/v1/dashboard/stats")
def get_dashboard_stats():
    """Estadísticas del dashboard (datos simulados)"""
    return {
        "total_vehiculos": 15,
        "vehiculos_disponibles": 8,
        "vehiculos_en_uso": 5,
        "vehiculos_mantenimiento": 2,
        "total_conductores": 12,
        "conductores_disponibles": 7,
        "solicitudes_pendientes": 3
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )