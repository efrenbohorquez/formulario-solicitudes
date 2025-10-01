from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, date, timedelta
from ...core.database import get_db
from ...database.models import (
    Vehicle, Driver, TransportRequest, Assignment, Maintenance, MaintenanceAlert,
    VehicleStatus, DriverStatus, RequestStatus, MaintenanceStatus, AlertPriority
)
from ...schemas.schemas import DashboardStats, VehicleAvailability
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Obtiene estadísticas generales para el dashboard"""
    
    # Estadísticas de vehículos
    total_vehiculos = db.query(Vehicle).filter(Vehicle.activo == True).count()
    vehiculos_disponibles = db.query(Vehicle).filter(
        Vehicle.activo == True,
        Vehicle.estado == VehicleStatus.DISPONIBLE
    ).count()
    vehiculos_en_uso = db.query(Vehicle).filter(
        Vehicle.activo == True,
        Vehicle.estado == VehicleStatus.EN_USO
    ).count()
    vehiculos_mantenimiento = db.query(Vehicle).filter(
        Vehicle.activo == True,
        Vehicle.estado == VehicleStatus.MANTENIMIENTO
    ).count()
    
    # Estadísticas de conductores
    total_conductores = db.query(Driver).filter(Driver.activo == True).count()
    conductores_disponibles = db.query(Driver).filter(
        Driver.activo == True,
        Driver.estado == DriverStatus.DISPONIBLE,
        Driver.fecha_vencimiento_licencia > date.today()
    ).count()
    
    # Estadísticas de solicitudes
    solicitudes_pendientes = db.query(TransportRequest).filter(
        TransportRequest.estado == RequestStatus.PENDIENTE
    ).count()
    
    # Alertas activas
    alertas_activas = db.query(MaintenanceAlert).filter(
        MaintenanceAlert.activa == True
    ).count()
    
    # Mantenimientos programados para los próximos 30 días
    future_date = datetime.now() + timedelta(days=30)
    mantenimientos_programados = db.query(Maintenance).filter(
        Maintenance.estado == MaintenanceStatus.PROGRAMADO,
        Maintenance.fecha_programada >= datetime.now(),
        Maintenance.fecha_programada <= future_date
    ).count()
    
    return DashboardStats(
        total_vehiculos=total_vehiculos,
        vehiculos_disponibles=vehiculos_disponibles,
        vehiculos_en_uso=vehiculos_en_uso,
        vehiculos_mantenimiento=vehiculos_mantenimiento,
        total_conductores=total_conductores,
        conductores_disponibles=conductores_disponibles,
        solicitudes_pendientes=solicitudes_pendientes,
        alertas_activas=alertas_activas,
        mantenimientos_programados=mantenimientos_programados
    )

@router.get("/alerts")
def get_dashboard_alerts(
    limit: int = Query(10, ge=1, le=50, description="Número máximo de alertas a retornar"),
    priority: Optional[AlertPriority] = Query(None, description="Filtrar por prioridad"),
    db: Session = Depends(get_db)
):
    """Obtiene alertas importantes para mostrar en el dashboard"""
    
    query = db.query(MaintenanceAlert).filter(
        MaintenanceAlert.activa == True
    )
    
    if priority:
        query = query.filter(MaintenanceAlert.prioridad == priority)
    
    alerts = query.order_by(
        MaintenanceAlert.prioridad.desc(),
        MaintenanceAlert.fecha_creacion.desc()
    ).limit(limit).all()
    
    # Contar alertas por prioridad
    alert_counts = {}
    for prio in AlertPriority:
        count = db.query(MaintenanceAlert).filter(
            MaintenanceAlert.activa == True,
            MaintenanceAlert.prioridad == prio
        ).count()
        alert_counts[prio.value] = count
    
    # Alertas de licencias próximas a vencer
    license_alerts = []
    drivers_expiring = db.query(Driver).filter(
        Driver.activo == True,
        Driver.fecha_vencimiento_licencia <= date.today() + timedelta(days=30),
        Driver.fecha_vencimiento_licencia > date.today()
    ).all()
    
    for driver in drivers_expiring:
        days_until = (driver.fecha_vencimiento_licencia - date.today()).days
        license_alerts.append({
            "type": "license_expiry",
            "driver_name": driver.nombre_completo,
            "driver_id": driver.id,
            "license_number": driver.numero_licencia,
            "days_until_expiry": days_until,
            "priority": "critica" if days_until <= 7 else "alta" if days_until <= 15 else "media"
        })
    
    return {
        "maintenance_alerts": alerts,
        "license_alerts": license_alerts,
        "alert_summary": alert_counts,
        "total_alerts": len(alerts) + len(license_alerts)
    }

@router.get("/vehicle-availability")
def get_vehicle_availability(
    fecha: Optional[date] = Query(None, description="Fecha para verificar disponibilidad (default: hoy)"),
    db: Session = Depends(get_db)
):
    """Obtiene disponibilidad de vehículos para una fecha específica"""
    
    target_date = fecha or date.today()
    
    # Obtener todos los vehículos activos
    vehicles = db.query(Vehicle).filter(Vehicle.activo == True).all()
    
    availability_list = []
    
    for vehicle in vehicles:
        # Verificar si tiene asignaciones en la fecha
        assignment = db.query(Assignment).join(TransportRequest).filter(
            Assignment.vehiculo_id == vehicle.id,
            func.date(TransportRequest.fecha_viaje) == target_date,
            TransportRequest.estado.in_([RequestStatus.ASIGNADO, RequestStatus.EN_CURSO])
        ).first()
        
        # Verificar mantenimientos programados
        maintenance = db.query(Maintenance).filter(
            Maintenance.vehiculo_id == vehicle.id,
            func.date(Maintenance.fecha_programada) == target_date,
            Maintenance.estado.in_([MaintenanceStatus.PROGRAMADO, MaintenanceStatus.EN_PROCESO])
        ).first()
        
        # Determinar estado de disponibilidad
        if maintenance:
            status = VehicleStatus.MANTENIMIENTO
        elif assignment:
            status = VehicleStatus.EN_USO
        else:
            status = VehicleStatus.DISPONIBLE
        
        # Próxima revisión (SOAT, técnico-mecánica, etc.)
        proxima_revision = None
        if vehicle.fecha_soat:
            if not proxima_revision or vehicle.fecha_soat < proxima_revision:
                proxima_revision = vehicle.fecha_soat
        if vehicle.fecha_tecnicomecanica:
            if not proxima_revision or vehicle.fecha_tecnicomecanica < proxima_revision:
                proxima_revision = vehicle.fecha_tecnicomecanica
        
        availability_list.append(VehicleAvailability(
            id=vehicle.id,
            placa=vehicle.placa,
            marca=vehicle.marca,
            modelo=vehicle.modelo,
            estado=status,
            kilometraje=vehicle.kilometraje or 0,
            proxima_revision=proxima_revision
        ))
    
    # Contar por estado
    summary = {
        "disponibles": len([v for v in availability_list if v.estado == VehicleStatus.DISPONIBLE]),
        "en_uso": len([v for v in availability_list if v.estado == VehicleStatus.EN_USO]),
        "mantenimiento": len([v for v in availability_list if v.estado == VehicleStatus.MANTENIMIENTO])
    }
    
    return {
        "date": target_date,
        "vehicle_availability": availability_list,
        "summary": summary
    }

@router.get("/recent-activity")
def get_recent_activity(
    limit: int = Query(10, ge=1, le=50, description="Número de actividades recientes"),
    db: Session = Depends(get_db)
):
    """Obtiene actividad reciente en el sistema"""
    
    activities = []
    
    # Solicitudes recientes
    recent_requests = db.query(TransportRequest).order_by(
        TransportRequest.created_at.desc()
    ).limit(limit//3).all()
    
    for req in recent_requests:
        activities.append({
            "type": "request_created",
            "timestamp": req.created_at,
            "description": f"Nueva solicitud: {req.nombre_solicitante} - {req.destino}",
            "entity_id": req.id,
            "priority": req.prioridad.value
        })
    
    # Asignaciones recientes
    recent_assignments = db.query(Assignment).order_by(
        Assignment.fecha_asignacion.desc()
    ).limit(limit//3).all()
    
    for assign in recent_assignments:
        vehicle = db.query(Vehicle).filter(Vehicle.id == assign.vehiculo_id).first()
        driver = db.query(Driver).filter(Driver.id == assign.conductor_id).first()
        activities.append({
            "type": "assignment_created",
            "timestamp": assign.fecha_asignacion,
            "description": f"Asignación creada: {vehicle.placa if vehicle else 'N/A'} - {driver.nombre_completo if driver else 'N/A'}",
            "entity_id": assign.id
        })
    
    # Mantenimientos recientes
    recent_maintenance = db.query(Maintenance).order_by(
        Maintenance.created_at.desc()
    ).limit(limit//3).all()
    
    for maint in recent_maintenance:
        vehicle = db.query(Vehicle).filter(Vehicle.id == maint.vehiculo_id).first()
        activities.append({
            "type": "maintenance_scheduled",
            "timestamp": maint.created_at,
            "description": f"Mantenimiento programado: {vehicle.placa if vehicle else 'N/A'} - {maint.tipo_mantenimiento.value}",
            "entity_id": maint.id
        })
    
    # Ordenar por timestamp y limitar
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    activities = activities[:limit]
    
    return {
        "recent_activities": activities,
        "total": len(activities)
    }

@router.get("/performance-metrics")
def get_performance_metrics(
    days_back: int = Query(30, ge=1, le=365, description="Días hacia atrás para calcular métricas"),
    db: Session = Depends(get_db)
):
    """Obtiene métricas de rendimiento del sistema"""
    
    start_date = datetime.now() - timedelta(days=days_back)
    
    # Métricas de solicitudes
    total_requests = db.query(TransportRequest).filter(
        TransportRequest.created_at >= start_date
    ).count()
    
    completed_requests = db.query(TransportRequest).filter(
        TransportRequest.created_at >= start_date,
        TransportRequest.estado == RequestStatus.COMPLETADO
    ).count()
    
    # Tiempo promedio de asignación (desde creación hasta asignación)
    avg_assignment_time_query = db.query(
        func.avg(
            func.julianday(Assignment.fecha_asignacion) - 
            func.julianday(TransportRequest.fecha_solicitud)
        ).label('avg_days')
    ).join(TransportRequest).filter(
        TransportRequest.created_at >= start_date,
        Assignment.fecha_asignacion.isnot(None)
    ).first()
    
    avg_assignment_time_days = avg_assignment_time_query.avg_days if avg_assignment_time_query.avg_days else 0
    
    # Utilización de vehículos (% de tiempo en uso)
    total_vehicles = db.query(Vehicle).filter(Vehicle.activo == True).count()
    
    # Días con asignaciones por vehículo
    vehicle_usage = db.query(
        func.count(func.distinct(func.date(TransportRequest.fecha_viaje))).label('days_used')
    ).join(Assignment).join(TransportRequest).filter(
        TransportRequest.fecha_viaje >= start_date,
        TransportRequest.estado.in_([RequestStatus.COMPLETADO, RequestStatus.EN_CURSO])
    ).first()
    
    vehicle_utilization = (vehicle_usage.days_used / (days_back * total_vehicles) * 100) if total_vehicles > 0 else 0
    
    # Costo promedio de mantenimiento
    avg_maintenance_cost = db.query(
        func.avg(Maintenance.costo_real)
    ).filter(
        Maintenance.fecha_finalizacion >= start_date,
        Maintenance.estado == MaintenanceStatus.COMPLETADO,
        Maintenance.costo_real.isnot(None)
    ).scalar() or 0
    
    # Eficiencia de combustible (km por vehículo)
    total_km = db.query(
        func.sum(Assignment.kilometraje_fin - Assignment.kilometraje_inicio)
    ).join(TransportRequest).filter(
        TransportRequest.fecha_viaje >= start_date,
        Assignment.kilometraje_fin.isnot(None),
        Assignment.kilometraje_inicio.isnot(None)
    ).scalar() or 0
    
    avg_km_per_vehicle = (total_km / total_vehicles) if total_vehicles > 0 else 0
    
    return {
        "period": {
            "start_date": start_date.date(),
            "end_date": date.today(),
            "days": days_back
        },
        "request_metrics": {
            "total_requests": total_requests,
            "completed_requests": completed_requests,
            "completion_rate": (completed_requests / total_requests * 100) if total_requests > 0 else 0,
            "avg_assignment_time_hours": avg_assignment_time_days * 24
        },
        "fleet_metrics": {
            "total_vehicles": total_vehicles,
            "vehicle_utilization_percent": vehicle_utilization,
            "avg_km_per_vehicle": avg_km_per_vehicle,
            "total_km_traveled": total_km
        },
        "maintenance_metrics": {
            "avg_maintenance_cost": float(avg_maintenance_cost)
        }
    }

@router.get("/upcoming-events")
def get_upcoming_events(
    days_ahead: int = Query(7, ge=1, le=30, description="Días hacia adelante para buscar eventos"),
    db: Session = Depends(get_db)
):
    """Obtiene eventos próximos (viajes programados, mantenimientos, vencimientos)"""
    
    end_date = datetime.now() + timedelta(days=days_ahead)
    
    events = []
    
    # Viajes programados
    upcoming_trips = db.query(Assignment).join(TransportRequest).filter(
        TransportRequest.fecha_viaje >= datetime.now(),
        TransportRequest.fecha_viaje <= end_date,
        TransportRequest.estado.in_([RequestStatus.ASIGNADO, RequestStatus.EN_CURSO])
    ).all()
    
    for trip in upcoming_trips:
        vehicle = db.query(Vehicle).filter(Vehicle.id == trip.vehiculo_id).first()
        driver = db.query(Driver).filter(Driver.id == trip.conductor_id).first()
        events.append({
            "type": "trip",
            "datetime": trip.solicitud.fecha_viaje,
            "title": f"Viaje programado",
            "description": f"{vehicle.placa if vehicle else 'N/A'} - {driver.nombre_completo if driver else 'N/A'}",
            "location": f"{trip.solicitud.origen} → {trip.solicitud.destino}",
            "priority": trip.solicitud.prioridad.value,
            "entity_id": trip.id
        })
    
    # Mantenimientos programados
    upcoming_maintenance = db.query(Maintenance).filter(
        Maintenance.fecha_programada >= datetime.now(),
        Maintenance.fecha_programada <= end_date,
        Maintenance.estado == MaintenanceStatus.PROGRAMADO
    ).all()
    
    for maint in upcoming_maintenance:
        vehicle = db.query(Vehicle).filter(Vehicle.id == maint.vehiculo_id).first()
        events.append({
            "type": "maintenance",
            "datetime": maint.fecha_programada,
            "title": f"Mantenimiento {maint.tipo_mantenimiento.value}",
            "description": f"{vehicle.placa if vehicle else 'N/A'} - {maint.descripcion}",
            "location": maint.taller_proveedor or "Por definir",
            "priority": "alta" if maint.tipo_mantenimiento.value in ["correctivo", "emergencia"] else "media",
            "entity_id": maint.id
        })
    
    # Vencimientos de documentos
    upcoming_expirations = []
    
    # SOAT próximos a vencer
    vehicles_soat = db.query(Vehicle).filter(
        Vehicle.activo == True,
        Vehicle.fecha_soat.isnot(None),
        Vehicle.fecha_soat >= date.today(),
        Vehicle.fecha_soat <= end_date.date()
    ).all()
    
    for vehicle in vehicles_soat:
        events.append({
            "type": "document_expiry",
            "datetime": datetime.combine(vehicle.fecha_soat, datetime.min.time()),
            "title": "Vencimiento SOAT",
            "description": f"Vehículo {vehicle.placa}",
            "priority": "critica" if (vehicle.fecha_soat - date.today()).days <= 3 else "alta",
            "entity_id": vehicle.id
        })
    
    # Ordenar eventos por fecha
    events.sort(key=lambda x: x["datetime"])
    
    return {
        "upcoming_events": events,
        "total": len(events),
        "period": {
            "start": datetime.now(),
            "end": end_date,
            "days_ahead": days_ahead
        }
    }

@router.get("/fleet-status")
def get_fleet_status(db: Session = Depends(get_db)):
    """Obtiene estado actual completo de la flota"""
    
    # Estado de vehículos por tipo
    vehicle_status_by_type = db.query(
        Vehicle.tipo_vehiculo,
        Vehicle.estado,
        func.count(Vehicle.id).label('count')
    ).filter(
        Vehicle.activo == True
    ).group_by(
        Vehicle.tipo_vehiculo, Vehicle.estado
    ).all()
    
    # Estado de conductores
    driver_status = db.query(
        Driver.estado,
        func.count(Driver.id).label('count')
    ).filter(
        Driver.activo == True,
        Driver.fecha_vencimiento_licencia > date.today()
    ).group_by(Driver.estado).all()
    
    # Solicitudes por estado
    request_status = db.query(
        TransportRequest.estado,
        func.count(TransportRequest.id).label('count')
    ).group_by(TransportRequest.estado).all()
    
    return {
        "vehicle_status_by_type": [
            {
                "tipo": item.tipo_vehiculo.value,
                "estado": item.estado.value,
                "count": item.count
            }
            for item in vehicle_status_by_type
        ],
        "driver_status": [
            {
                "estado": item.estado.value,
                "count": item.count
            }
            for item in driver_status
        ],
        "request_status": [
            {
                "estado": item.estado.value,
                "count": item.count
            }
            for item in request_status
        ],
        "timestamp": datetime.now()
    }