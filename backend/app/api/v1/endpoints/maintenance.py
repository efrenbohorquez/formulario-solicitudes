from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...database.models import Maintenance, MaintenanceStatus, MaintenanceType, Vehicle
from ...schemas.schemas import (
    Maintenance as MaintenanceSchema,
    MaintenanceCreate,
    MaintenanceUpdate,
    PaginatedResponse
)
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
def get_maintenance_records(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(20, ge=1, le=100, description="Número de registros a retornar"),
    vehiculo_id: Optional[int] = Query(None, description="Filtrar por vehículo"),
    tipo: Optional[MaintenanceType] = Query(None, description="Filtrar por tipo de mantenimiento"),
    estado: Optional[MaintenanceStatus] = Query(None, description="Filtrar por estado"),
    fecha_desde: Optional[date] = Query(None, description="Filtrar desde fecha"),
    fecha_hasta: Optional[date] = Query(None, description="Filtrar hasta fecha"),
    db: Session = Depends(get_db)
):
    """Obtiene lista de mantenimientos con filtros y paginación"""
    
    query = db.query(Maintenance)
    
    # Aplicar filtros
    if vehiculo_id:
        query = query.filter(Maintenance.vehiculo_id == vehiculo_id)
    if tipo:
        query = query.filter(Maintenance.tipo_mantenimiento == tipo)
    if estado:
        query = query.filter(Maintenance.estado == estado)
    if fecha_desde:
        query = query.filter(Maintenance.fecha_programada >= fecha_desde)
    if fecha_hasta:
        fecha_hasta_end = datetime.combine(fecha_hasta, datetime.max.time())
        query = query.filter(Maintenance.fecha_programada <= fecha_hasta_end)
    
    # Ordenar por fecha programada descendente
    query = query.order_by(Maintenance.fecha_programada.desc())
    
    # Obtener total de registros
    total = query.count()
    
    # Aplicar paginación
    maintenance_records = query.offset(skip).limit(limit).all()
    
    # Calcular páginas
    pages = (total + limit - 1) // limit
    current_page = (skip // limit) + 1
    
    return PaginatedResponse(
        items=[MaintenanceSchema.model_validate(m) for m in maintenance_records],
        total=total,
        page=current_page,
        pages=pages,
        per_page=limit
    )

@router.get("/{maintenance_id}", response_model=MaintenanceSchema)
def get_maintenance(maintenance_id: int, db: Session = Depends(get_db)):
    """Obtiene un registro de mantenimiento específico por ID"""
    
    maintenance = db.query(Maintenance).filter(
        Maintenance.id == maintenance_id
    ).first()
    
    if not maintenance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de mantenimiento no encontrado"
        )
    
    return MaintenanceSchema.model_validate(maintenance)

@router.post("/", response_model=MaintenanceSchema, status_code=status.HTTP_201_CREATED)
def create_maintenance(maintenance: MaintenanceCreate, db: Session = Depends(get_db)):
    """Programa un nuevo mantenimiento"""
    
    # Verificar que el vehículo existe
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == maintenance.vehiculo_id,
        Vehicle.activo == True
    ).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado"
        )
    
    # Validar que la fecha programada sea futura para mantenimientos preventivos
    if (maintenance.tipo_mantenimiento == MaintenanceType.PREVENTIVO and 
        maintenance.fecha_programada <= datetime.now()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de mantenimiento preventivo debe ser futura"
        )
    
    # Crear nuevo mantenimiento
    db_maintenance = Maintenance(**maintenance.model_dump())
    db_maintenance.created_at = datetime.now()
    
    # Si es mantenimiento correctivo o de emergencia, marcar vehículo como en mantenimiento
    if maintenance.tipo_mantenimiento in [MaintenanceType.CORRECTIVO, MaintenanceType.EMERGENCIA]:
        from ...database.models import VehicleStatus
        vehicle.estado = VehicleStatus.MANTENIMIENTO
    
    db.add(db_maintenance)
    db.commit()
    db.refresh(db_maintenance)
    
    logger.info(f"Mantenimiento programado: Vehículo {vehicle.placa} - {maintenance.tipo_mantenimiento.value} (ID: {db_maintenance.id})")
    
    return MaintenanceSchema.model_validate(db_maintenance)

@router.put("/{maintenance_id}", response_model=MaintenanceSchema)
def update_maintenance(
    maintenance_id: int, 
    maintenance_update: MaintenanceUpdate, 
    db: Session = Depends(get_db)
):
    """Actualiza un registro de mantenimiento existente"""
    
    # Buscar mantenimiento
    db_maintenance = db.query(Maintenance).filter(
        Maintenance.id == maintenance_id
    ).first()
    
    if not db_maintenance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de mantenimiento no encontrado"
        )
    
    # Obtener vehículo asociado
    vehicle = db.query(Vehicle).filter(Vehicle.id == db_maintenance.vehiculo_id).first()
    
    # Actualizar campos
    update_data = maintenance_update.model_dump(exclude_unset=True)
    old_status = db_maintenance.estado
    
    for field, value in update_data.items():
        setattr(db_maintenance, field, value)
    
    db_maintenance.updated_at = datetime.now()
    
    # Manejar cambios de estado
    if maintenance_update.estado and maintenance_update.estado != old_status:
        await handle_maintenance_status_change(db, db_maintenance, vehicle, old_status)
    
    db.commit()
    db.refresh(db_maintenance)
    
    logger.info(f"Mantenimiento actualizado: ID {db_maintenance.id} - {db_maintenance.estado.value}")
    
    return MaintenanceSchema.model_validate(db_maintenance)

async def handle_maintenance_status_change(
    db: Session, 
    maintenance: Maintenance, 
    vehicle: Vehicle, 
    old_status: MaintenanceStatus
):
    """Maneja cambios de estado en el mantenimiento y actualiza el vehículo"""
    
    from ...database.models import VehicleStatus
    
    if maintenance.estado == MaintenanceStatus.EN_PROCESO:
        # Mantenimiento iniciado
        vehicle.estado = VehicleStatus.MANTENIMIENTO
        if not maintenance.fecha_inicio:
            maintenance.fecha_inicio = datetime.now()
    
    elif maintenance.estado == MaintenanceStatus.COMPLETADO:
        # Mantenimiento completado
        vehicle.estado = VehicleStatus.DISPONIBLE
        if not maintenance.fecha_finalizacion:
            maintenance.fecha_finalizacion = datetime.now()
        
        # Actualizar kilometraje si se proporcionó
        if maintenance.kilometraje_actual and maintenance.kilometraje_actual > vehicle.kilometraje:
            vehicle.kilometraje = maintenance.kilometraje_actual
        
        # Calcular próximo mantenimiento si no se especificó
        if not maintenance.proximo_mantenimiento_km and vehicle.kilometraje:
            maintenance.proximo_mantenimiento_km = vehicle.kilometraje + 10000  # Default: cada 10k km
    
    elif maintenance.estado == MaintenanceStatus.CANCELADO:
        # Mantenimiento cancelado - volver a estado anterior del vehículo
        vehicle.estado = VehicleStatus.DISPONIBLE

@router.delete("/{maintenance_id}")
def delete_maintenance(maintenance_id: int, db: Session = Depends(get_db)):
    """Cancela un mantenimiento programado"""
    
    db_maintenance = db.query(Maintenance).filter(
        Maintenance.id == maintenance_id
    ).first()
    
    if not db_maintenance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de mantenimiento no encontrado"
        )
    
    # Solo permitir cancelación si está programado o en proceso
    if db_maintenance.estado in [MaintenanceStatus.COMPLETADO]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede cancelar un mantenimiento completado"
        )
    
    # Marcar como cancelado
    db_maintenance.estado = MaintenanceStatus.CANCELADO
    db_maintenance.updated_at = datetime.now()
    
    # Actualizar estado del vehículo
    vehicle = db.query(Vehicle).filter(Vehicle.id == db_maintenance.vehiculo_id).first()
    if vehicle:
        from ...database.models import VehicleStatus
        vehicle.estado = VehicleStatus.DISPONIBLE
    
    db.commit()
    
    logger.info(f"Mantenimiento cancelado: ID {db_maintenance.id}")
    
    return {"message": "Mantenimiento cancelado exitosamente"}

@router.get("/scheduled/")
def get_scheduled_maintenance(
    dias_adelante: int = Query(30, ge=1, le=365, description="Días hacia adelante para buscar mantenimientos"),
    vehiculo_id: Optional[int] = Query(None, description="Filtrar por vehículo específico"),
    tipo: Optional[MaintenanceType] = Query(None, description="Filtrar por tipo de mantenimiento"),
    db: Session = Depends(get_db)
):
    """Obtiene mantenimientos programados en los próximos días"""
    
    from datetime import timedelta
    
    future_date = datetime.now() + timedelta(days=dias_adelante)
    
    query = db.query(Maintenance).filter(
        Maintenance.estado == MaintenanceStatus.PROGRAMADO,
        Maintenance.fecha_programada >= datetime.now(),
        Maintenance.fecha_programada <= future_date
    )
    
    if vehiculo_id:
        query = query.filter(Maintenance.vehiculo_id == vehiculo_id)
    if tipo:
        query = query.filter(Maintenance.tipo_mantenimiento == tipo)
    
    scheduled_maintenance = query.order_by(Maintenance.fecha_programada).all()
    
    # Agrupar por urgencia
    upcoming = []
    for maintenance in scheduled_maintenance:
        days_until = (maintenance.fecha_programada.date() - datetime.now().date()).days
        
        if days_until <= 3:
            urgency = "inmediato"
        elif days_until <= 7:
            urgency = "esta_semana"
        elif days_until <= 30:
            urgency = "este_mes"
        else:
            urgency = "futuro"
        
        maintenance_data = MaintenanceSchema.model_validate(maintenance).model_dump()
        maintenance_data["days_until"] = days_until
        maintenance_data["urgency"] = urgency
        upcoming.append(maintenance_data)
    
    return {
        "scheduled_maintenance": upcoming,
        "total": len(upcoming),
        "summary": {
            "inmediato": len([m for m in upcoming if m["urgency"] == "inmediato"]),
            "esta_semana": len([m for m in upcoming if m["urgency"] == "esta_semana"]),
            "este_mes": len([m for m in upcoming if m["urgency"] == "este_mes"]),
            "futuro": len([m for m in upcoming if m["urgency"] == "futuro"])
        },
        "dias_adelante": dias_adelante
    }

@router.get("/overdue/")
def get_overdue_maintenance(
    vehiculo_id: Optional[int] = Query(None, description="Filtrar por vehículo específico"),
    db: Session = Depends(get_db)
):
    """Obtiene mantenimientos vencidos (no realizados en su fecha programada)"""
    
    query = db.query(Maintenance).filter(
        Maintenance.estado == MaintenanceStatus.PROGRAMADO,
        Maintenance.fecha_programada < datetime.now()
    )
    
    if vehiculo_id:
        query = query.filter(Maintenance.vehiculo_id == vehiculo_id)
    
    overdue_maintenance = query.order_by(Maintenance.fecha_programada).all()
    
    # Calcular días de retraso
    overdue_with_delay = []
    for maintenance in overdue_maintenance:
        days_overdue = (datetime.now().date() - maintenance.fecha_programada.date()).days
        
        if days_overdue <= 7:
            priority = "media"
        elif days_overdue <= 30:
            priority = "alta"
        else:
            priority = "critica"
        
        maintenance_data = MaintenanceSchema.model_validate(maintenance).model_dump()
        maintenance_data["days_overdue"] = days_overdue
        maintenance_data["priority"] = priority
        overdue_with_delay.append(maintenance_data)
    
    return {
        "overdue_maintenance": overdue_with_delay,
        "total": len(overdue_with_delay),
        "summary": {
            "media": len([m for m in overdue_with_delay if m["priority"] == "media"]),
            "alta": len([m for m in overdue_with_delay if m["priority"] == "alta"]),
            "critica": len([m for m in overdue_with_delay if m["priority"] == "critica"])
        }
    }

@router.get("/costs/")
def get_maintenance_costs(
    vehiculo_id: Optional[int] = Query(None, description="Filtrar por vehículo específico"),
    fecha_desde: Optional[date] = Query(None, description="Fecha inicio"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha fin"),
    db: Session = Depends(get_db)
):
    """Obtiene análisis de costos de mantenimiento"""
    
    from sqlalchemy import func
    
    query = db.query(Maintenance).filter(
        Maintenance.estado == MaintenanceStatus.COMPLETADO,
        Maintenance.costo_real.isnot(None)
    )
    
    if vehiculo_id:
        query = query.filter(Maintenance.vehiculo_id == vehiculo_id)
    if fecha_desde:
        query = query.filter(Maintenance.fecha_finalizacion >= fecha_desde)
    if fecha_hasta:
        fecha_hasta_end = datetime.combine(fecha_hasta, datetime.max.time())
        query = query.filter(Maintenance.fecha_finalizacion <= fecha_hasta_end)
    
    # Estadísticas básicas
    total_maintenance = query.count()
    total_cost = query.with_entities(func.sum(Maintenance.costo_real)).scalar() or 0
    avg_cost = query.with_entities(func.avg(Maintenance.costo_real)).scalar() or 0
    
    # Costos por tipo de mantenimiento
    costs_by_type = {}
    for tipo in MaintenanceType:
        type_cost = query.filter(
            Maintenance.tipo_mantenimiento == tipo
        ).with_entities(func.sum(Maintenance.costo_real)).scalar() or 0
        costs_by_type[tipo.value] = float(type_cost)
    
    # Top vehículos por costo de mantenimiento
    top_vehicles = query.join(Vehicle).with_entities(
        Vehicle.placa,
        Vehicle.marca,
        Vehicle.modelo,
        func.sum(Maintenance.costo_real).label('total_cost'),
        func.count(Maintenance.id).label('maintenance_count')
    ).group_by(
        Vehicle.id, Vehicle.placa, Vehicle.marca, Vehicle.modelo
    ).order_by(
        func.sum(Maintenance.costo_real).desc()
    ).limit(10).all()
    
    return {
        "period": {
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta
        },
        "summary": {
            "total_maintenance": total_maintenance,
            "total_cost": float(total_cost),
            "average_cost": float(avg_cost)
        },
        "costs_by_type": costs_by_type,
        "top_vehicles_by_cost": [
            {
                "placa": v[0],
                "marca": v[1],
                "modelo": v[2],
                "total_cost": float(v[3]),
                "maintenance_count": v[4]
            }
            for v in top_vehicles
        ]
    }