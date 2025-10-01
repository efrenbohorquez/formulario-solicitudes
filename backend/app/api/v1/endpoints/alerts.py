from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, date, timedelta
from ...core.database import get_db
from ...database.models import (
    Vehicle, Driver, MaintenanceAlert, Maintenance, User,
    VehicleStatus, DriverStatus, MaintenanceStatus, AlertPriority, UserRole
)
from ...schemas.schemas import (
    MaintenanceAlert as MaintenanceAlertSchema,
    MaintenanceAlertCreate, 
    MaintenanceAlertUpdate
)
from .auth import get_current_active_user, require_role
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[MaintenanceAlertSchema])
def get_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    priority: Optional[AlertPriority] = Query(None, description="Filtrar por prioridad"),
    active_only: bool = Query(True, description="Solo alertas activas"),
    vehicle_id: Optional[int] = Query(None, description="Filtrar por vehículo"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene lista de alertas con filtros opcionales"""
    
    query = db.query(MaintenanceAlert)
    
    if active_only:
        query = query.filter(MaintenanceAlert.activa == True)
    
    if priority:
        query = query.filter(MaintenanceAlert.prioridad == priority)
    
    if vehicle_id:
        query = query.filter(MaintenanceAlert.vehiculo_id == vehicle_id)
    
    alerts = query.order_by(
        MaintenanceAlert.prioridad.desc(),
        MaintenanceAlert.fecha_creacion.desc()
    ).offset(skip).limit(limit).all()
    
    return alerts

@router.post("/", response_model=MaintenanceAlertSchema)
def create_alert(
    alert_data: MaintenanceAlertCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPERVISOR])),
    db: Session = Depends(get_db)
):
    """Crea una nueva alerta de mantenimiento"""
    
    # Verificar que el vehículo existe
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == alert_data.vehiculo_id,
        Vehicle.activo == True
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado o inactivo"
        )
    
    # Crear la alerta
    db_alert = MaintenanceAlert(
        vehiculo_id=alert_data.vehiculo_id,
        tipo_alerta=alert_data.tipo_alerta,
        mensaje=alert_data.mensaje,
        prioridad=alert_data.prioridad,
        fecha_vencimiento=alert_data.fecha_vencimiento,
        fecha_creacion=datetime.utcnow(),
        activa=True,
        vista=False
    )
    
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    logger.info(f"Alerta creada ID: {db_alert.id} para vehículo {vehicle.placa} por {current_user.username}")
    
    return db_alert

@router.get("/{alert_id}", response_model=MaintenanceAlertSchema)
def get_alert(
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene una alerta específica por ID"""
    
    alert = db.query(MaintenanceAlert).filter(MaintenanceAlert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada"
        )
    
    return alert

@router.put("/{alert_id}/mark-seen")
def mark_alert_as_seen(
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Marca una alerta como vista"""
    
    alert = db.query(MaintenanceAlert).filter(MaintenanceAlert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada"
        )
    
    alert.vista = True
    db.commit()
    
    logger.info(f"Alerta {alert_id} marcada como vista por {current_user.username}")
    
    return {"message": "Alerta marcada como vista"}

@router.put("/{alert_id}/deactivate")
def deactivate_alert(
    alert_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPERVISOR])),
    db: Session = Depends(get_db)
):
    """Desactiva una alerta"""
    
    alert = db.query(MaintenanceAlert).filter(MaintenanceAlert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada"
        )
    
    alert.activa = False
    db.commit()
    
    logger.info(f"Alerta {alert_id} desactivada por {current_user.username}")
    
    return {"message": "Alerta desactivada"}

@router.get("/vehicle/{vehicle_id}", response_model=List[MaintenanceAlertSchema])
def get_alerts_by_vehicle(
    vehicle_id: int,
    active_only: bool = Query(True, description="Solo alertas activas"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene todas las alertas de un vehículo específico"""
    
    # Verificar que el vehículo existe
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado"
        )
    
    query = db.query(MaintenanceAlert).filter(MaintenanceAlert.vehiculo_id == vehicle_id)
    
    if active_only:
        query = query.filter(MaintenanceAlert.activa == True)
    
    alerts = query.order_by(
        MaintenanceAlert.prioridad.desc(),
        MaintenanceAlert.fecha_creacion.desc()
    ).all()
    
    return alerts

@router.get("/priority/{priority_level}", response_model=List[MaintenanceAlertSchema])
def get_alerts_by_priority(
    priority_level: AlertPriority,
    active_only: bool = Query(True, description="Solo alertas activas"),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene alertas por nivel de prioridad"""
    
    query = db.query(MaintenanceAlert).filter(MaintenanceAlert.prioridad == priority_level)
    
    if active_only:
        query = query.filter(MaintenanceAlert.activa == True)
    
    alerts = query.order_by(MaintenanceAlert.fecha_creacion.desc()).limit(limit).all()
    
    return alerts

@router.post("/check-expired-documents")
def check_expired_documents(
    days_ahead: int = Query(30, ge=1, le=365, description="Días de anticipación para alertas"),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPERVISOR])),
    db: Session = Depends(get_db)
):
    """Verifica documentos próximos a vencer y crea alertas automáticamente"""
    
    target_date = date.today() + timedelta(days=days_ahead)
    alerts_created = []
    
    # Verificar SOAT próximos a vencer
    vehicles_soat = db.query(Vehicle).filter(
        Vehicle.activo == True,
        Vehicle.fecha_soat.isnot(None),
        Vehicle.fecha_soat <= target_date,
        Vehicle.fecha_soat > date.today()
    ).all()
    
    for vehicle in vehicles_soat:
        days_until = (vehicle.fecha_soat - date.today()).days
        
        # Verificar si ya existe alerta activa para este vehículo y tipo
        existing_alert = db.query(MaintenanceAlert).filter(
            MaintenanceAlert.vehiculo_id == vehicle.id,
            MaintenanceAlert.tipo_alerta == "soat_vencimiento",
            MaintenanceAlert.activa == True
        ).first()
        
        if not existing_alert:
            priority = AlertPriority.CRITICA if days_until <= 7 else AlertPriority.ALTA
            
            alert = MaintenanceAlert(
                vehiculo_id=vehicle.id,
                tipo_alerta="soat_vencimiento",
                mensaje=f"SOAT del vehículo {vehicle.placa} vence el {vehicle.fecha_soat} ({days_until} días)",
                prioridad=priority,
                fecha_vencimiento=datetime.combine(vehicle.fecha_soat, datetime.min.time()),
                fecha_creacion=datetime.utcnow(),
                activa=True,
                vista=False
            )
            
            db.add(alert)
            alerts_created.append({
                "vehicle": vehicle.placa,
                "type": "SOAT",
                "expiry_date": vehicle.fecha_soat,
                "days_until": days_until
            })
    
    # Verificar revisiones técnico-mecánicas próximas a vencer
    vehicles_tecnico = db.query(Vehicle).filter(
        Vehicle.activo == True,
        Vehicle.fecha_tecnicomecanica.isnot(None),
        Vehicle.fecha_tecnicomecanica <= target_date,
        Vehicle.fecha_tecnicomecanica > date.today()
    ).all()
    
    for vehicle in vehicles_tecnico:
        days_until = (vehicle.fecha_tecnicomecanica - date.today()).days
        
        existing_alert = db.query(MaintenanceAlert).filter(
            MaintenanceAlert.vehiculo_id == vehicle.id,
            MaintenanceAlert.tipo_alerta == "tecnicomecanica_vencimiento",
            MaintenanceAlert.activa == True
        ).first()
        
        if not existing_alert:
            priority = AlertPriority.CRITICA if days_until <= 7 else AlertPriority.ALTA
            
            alert = MaintenanceAlert(
                vehiculo_id=vehicle.id,
                tipo_alerta="tecnicomecanica_vencimiento",
                mensaje=f"Revisión técnico-mecánica del vehículo {vehicle.placa} vence el {vehicle.fecha_tecnicomecanica} ({days_until} días)",
                prioridad=priority,
                fecha_vencimiento=datetime.combine(vehicle.fecha_tecnicomecanica, datetime.min.time()),
                fecha_creacion=datetime.utcnow(),
                activa=True,
                vista=False
            )
            
            db.add(alert)
            alerts_created.append({
                "vehicle": vehicle.placa,
                "type": "Revisión Técnico-mecánica",
                "expiry_date": vehicle.fecha_tecnicomecanica,
                "days_until": days_until
            })
    
    # Verificar licencias de conductores próximas a vencer
    drivers_expiring = db.query(Driver).filter(
        Driver.activo == True,
        Driver.fecha_vencimiento_licencia <= target_date,
        Driver.fecha_vencimiento_licencia > date.today()
    ).all()
    
    driver_alerts = []
    for driver in drivers_expiring:
        days_until = (driver.fecha_vencimiento_licencia - date.today()).days
        driver_alerts.append({
            "driver": driver.nombre_completo,
            "license_number": driver.numero_licencia,
            "expiry_date": driver.fecha_vencimiento_licencia,
            "days_until": days_until
        })
    
    db.commit()
    
    logger.info(f"Verificación de documentos vencidos ejecutada por {current_user.username}. "
               f"Alertas creadas: {len(alerts_created)}")
    
    return {
        "message": f"Verificación completada. {len(alerts_created)} nuevas alertas creadas.",
        "vehicle_alerts_created": alerts_created,
        "driver_alerts_found": driver_alerts,
        "total_new_alerts": len(alerts_created)
    }

@router.post("/check-maintenance-due")
def check_maintenance_due(
    km_threshold: int = Query(5000, ge=1000, le=20000, description="Umbral de kilómetros para alerta"),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPERVISOR])),
    db: Session = Depends(get_db)
):
    """Verifica vehículos que necesitan mantenimiento por kilometraje"""
    
    alerts_created = []
    
    # Obtener vehículos activos con información de mantenimiento
    vehicles = db.query(Vehicle).filter(Vehicle.activo == True).all()
    
    for vehicle in vehicles:
        if not vehicle.kilometraje:
            continue
        
        # Buscar último mantenimiento completado
        last_maintenance = db.query(Maintenance).filter(
            Maintenance.vehiculo_id == vehicle.id,
            Maintenance.estado == MaintenanceStatus.COMPLETADO
        ).order_by(Maintenance.fecha_finalizacion.desc()).first()
        
        # Determinar kilometraje del último mantenimiento
        last_km = 0
        if last_maintenance and last_maintenance.kilometraje_actual:
            last_km = last_maintenance.kilometraje_actual
        
        # Calcular kilómetros desde último mantenimiento
        km_since_maintenance = vehicle.kilometraje - last_km
        
        # Verificar si necesita mantenimiento
        if km_since_maintenance >= km_threshold:
            # Verificar si ya existe alerta activa
            existing_alert = db.query(MaintenanceAlert).filter(
                MaintenanceAlert.vehiculo_id == vehicle.id,
                MaintenanceAlert.tipo_alerta == "mantenimiento_kilometraje",
                MaintenanceAlert.activa == True
            ).first()
            
            if not existing_alert:
                priority = AlertPriority.ALTA if km_since_maintenance >= (km_threshold * 1.2) else AlertPriority.MEDIA
                
                alert = MaintenanceAlert(
                    vehiculo_id=vehicle.id,
                    tipo_alerta="mantenimiento_kilometraje",
                    mensaje=f"Vehículo {vehicle.placa} necesita mantenimiento. "
                           f"Kilómetros desde último mantenimiento: {km_since_maintenance:,} km",
                    prioridad=priority,
                    fecha_creacion=datetime.utcnow(),
                    activa=True,
                    vista=False
                )
                
                db.add(alert)
                alerts_created.append({
                    "vehicle": vehicle.placa,
                    "current_km": vehicle.kilometraje,
                    "last_maintenance_km": last_km,
                    "km_since_maintenance": km_since_maintenance
                })
    
    db.commit()
    
    logger.info(f"Verificación de mantenimiento por kilometraje ejecutada por {current_user.username}. "
               f"Alertas creadas: {len(alerts_created)}")
    
    return {
        "message": f"Verificación completada. {len(alerts_created)} nuevas alertas de mantenimiento creadas.",
        "alerts_created": alerts_created,
        "km_threshold": km_threshold
    }

@router.get("/summary/stats")
def get_alert_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene estadísticas resumidas de alertas"""
    
    # Contar alertas por prioridad
    alert_stats = {}
    for priority in AlertPriority:
        count = db.query(MaintenanceAlert).filter(
            MaintenanceAlert.prioridad == priority,
            MaintenanceAlert.activa == True
        ).count()
        alert_stats[priority.value] = count
    
    # Alertas no vistas
    unseen_alerts = db.query(MaintenanceAlert).filter(
        MaintenanceAlert.activa == True,
        MaintenanceAlert.vista == False
    ).count()
    
    # Alertas por tipo
    alert_types = db.query(
        MaintenanceAlert.tipo_alerta,
        func.count(MaintenanceAlert.id).label('count')
    ).filter(
        MaintenanceAlert.activa == True
    ).group_by(MaintenanceAlert.tipo_alerta).all()
    
    type_stats = {item.tipo_alerta: item.count for item in alert_types}
    
    return {
        "active_alerts_by_priority": alert_stats,
        "unseen_alerts": unseen_alerts,
        "alerts_by_type": type_stats,
        "total_active_alerts": sum(alert_stats.values())
    }