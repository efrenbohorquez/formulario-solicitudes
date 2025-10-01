from fastapi import APIRouter
from .endpoints import vehicles, drivers, maintenance, requests, assignments, dashboard, auth, alerts

api_router = APIRouter()

# Incluir todos los routers de endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["Vehículos"])
api_router.include_router(drivers.router, prefix="/drivers", tags=["Conductores"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["Mantenimientos"])
api_router.include_router(requests.router, prefix="/requests", tags=["Solicitudes"])
api_router.include_router(assignments.router, prefix="/assignments", tags=["Asignaciones"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alertas"])