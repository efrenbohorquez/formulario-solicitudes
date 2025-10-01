from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ....core.database import get_db
from ....database.models import Vehicle, VehicleStatus, VehicleType
from ....schemas.schemas import (
    Vehicle as VehicleSchema,
    VehicleCreate,
    VehicleUpdate,
    PaginatedResponse
)
from ....services.notification_service import notification_service
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
def get_vehicles(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(20, ge=1, le=100, description="Número de registros a retornar"),
    placa: Optional[str] = Query(None, description="Filtrar por placa"),
    estado: Optional[VehicleStatus] = Query(None, description="Filtrar por estado"),
    tipo: Optional[VehicleType] = Query(None, description="Filtrar por tipo de vehículo"),
    marca: Optional[str] = Query(None, description="Filtrar por marca"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    db: Session = Depends(get_db)
):
    """Obtiene lista de vehículos con filtros y paginación"""
    
    query = db.query(Vehicle)
    
    # Aplicar filtros
    if placa:
        query = query.filter(Vehicle.placa.ilike(f"%{placa}%"))
    if estado:
        query = query.filter(Vehicle.estado == estado)
    if tipo:
        query = query.filter(Vehicle.tipo_vehiculo == tipo)
    if marca:
        query = query.filter(Vehicle.marca.ilike(f"%{marca}%"))
    if activo is not None:
        query = query.filter(Vehicle.activo == activo)
    
    # Obtener total de registros
    total = query.count()
    
    # Aplicar paginación
    vehicles = query.offset(skip).limit(limit).all()
    
    # Calcular páginas
    pages = (total + limit - 1) // limit
    current_page = (skip // limit) + 1
    
    return PaginatedResponse(
        items=[VehicleSchema.model_validate(v) for v in vehicles],
        total=total,
        page=current_page,
        pages=pages,
        per_page=limit
    )

@router.get("/{vehicle_id}", response_model=VehicleSchema)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    """Obtiene un vehículo específico por ID"""
    
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.activo == True
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado"
        )
    
    return VehicleSchema.model_validate(vehicle)

@router.post("/", response_model=VehicleSchema, status_code=status.HTTP_201_CREATED)
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    """Crea un nuevo vehículo"""
    
    # Verificar que la placa no exista
    existing_vehicle = db.query(Vehicle).filter(Vehicle.placa == vehicle.placa).first()
    if existing_vehicle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un vehículo con esta placa"
        )
    
    # Crear nuevo vehículo
    db_vehicle = Vehicle(**vehicle.model_dump())
    db_vehicle.created_at = datetime.now()
    
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    
    logger.info(f"Vehículo creado: {db_vehicle.placa} (ID: {db_vehicle.id})")
    
    return VehicleSchema.model_validate(db_vehicle)

@router.put("/{vehicle_id}", response_model=VehicleSchema)
def update_vehicle(
    vehicle_id: int, 
    vehicle_update: VehicleUpdate, 
    db: Session = Depends(get_db)
):
    """Actualiza un vehículo existente"""
    
    # Buscar vehículo
    db_vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.activo == True
    ).first()
    
    if not db_vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado"
        )
    
    # Si se actualiza la placa, verificar que no exista
    if vehicle_update.placa and vehicle_update.placa != db_vehicle.placa:
        existing_vehicle = db.query(Vehicle).filter(
            Vehicle.placa == vehicle_update.placa,
            Vehicle.id != vehicle_id
        ).first()
        if existing_vehicle:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un vehículo con esta placa"
            )
    
    # Actualizar campos
    update_data = vehicle_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_vehicle, field, value)
    
    db_vehicle.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_vehicle)
    
    logger.info(f"Vehículo actualizado: {db_vehicle.placa} (ID: {db_vehicle.id})")
    
    return VehicleSchema.model_validate(db_vehicle)

@router.delete("/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    """Elimina (desactiva) un vehículo"""
    
    db_vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.activo == True
    ).first()
    
    if not db_vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado"
        )
    
    # Verificar si tiene asignaciones activas
    # TODO: Implementar verificación de asignaciones activas
    
    # Soft delete - marcar como inactivo
    db_vehicle.activo = False
    db_vehicle.updated_at = datetime.now()
    
    db.commit()
    
    logger.info(f"Vehículo eliminado: {db_vehicle.placa} (ID: {db_vehicle.id})")
    
    return {"message": "Vehículo eliminado exitosamente"}

@router.get("/{vehicle_id}/maintenance-history")
def get_vehicle_maintenance_history(
    vehicle_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Obtiene el historial de mantenimiento de un vehículo"""
    
    # Verificar que el vehículo existe
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.activo == True
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado"
        )
    
    # Obtener historial de mantenimiento
    from ...database.models import Maintenance
    
    maintenance_query = db.query(Maintenance).filter(
        Maintenance.vehiculo_id == vehicle_id
    ).order_by(Maintenance.fecha_programada.desc())
    
    total = maintenance_query.count()
    maintenance_records = maintenance_query.offset(skip).limit(limit).all()
    
    return {
        "vehicle": VehicleSchema.model_validate(vehicle),
        "maintenance_history": maintenance_records,
        "total": total,
        "page": (skip // limit) + 1,
        "pages": (total + limit - 1) // limit
    }

@router.get("/{vehicle_id}/alerts")
def get_vehicle_alerts(
    vehicle_id: int,
    active_only: bool = Query(True, description="Solo alertas activas"),
    db: Session = Depends(get_db)
):
    """Obtiene las alertas de un vehículo específico"""
    
    # Verificar que el vehículo existe
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.activo == True
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado"
        )
    
    # Obtener alertas
    from ...database.models import MaintenanceAlert
    
    alerts_query = db.query(MaintenanceAlert).filter(
        MaintenanceAlert.vehiculo_id == vehicle_id
    )
    
    if active_only:
        alerts_query = alerts_query.filter(MaintenanceAlert.activa == True)
    
    alerts = alerts_query.order_by(
        MaintenanceAlert.prioridad.desc(),
        MaintenanceAlert.fecha_creacion.desc()
    ).all()
    
    return {
        "vehicle": VehicleSchema.model_validate(vehicle),
        "alerts": alerts,
        "total_alerts": len(alerts),
        "active_alerts": len([a for a in alerts if a.activa])
    }

@router.post("/{vehicle_id}/update-mileage")
def update_vehicle_mileage(
    vehicle_id: int,
    new_mileage: int = Query(..., ge=0, description="Nuevo kilometraje"),
    db: Session = Depends(get_db)
):
    """Actualiza el kilometraje de un vehículo y verifica alertas de mantenimiento"""
    
    # Buscar vehículo
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.activo == True
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado"
        )
    
    # Validar que el nuevo kilometraje sea mayor al actual
    if new_mileage < vehicle.kilometraje:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nuevo kilometraje debe ser mayor al actual"
        )
    
    # Actualizar kilometraje
    old_mileage = vehicle.kilometraje
    vehicle.kilometraje = new_mileage
    vehicle.updated_at = datetime.now()
    
    db.commit()
    
    # Verificar alertas de mantenimiento
    notification_service._check_vehicle_maintenance_due(db, vehicle)
    db.commit()
    
    logger.info(f"Kilometraje actualizado para vehículo {vehicle.placa}: {old_mileage} -> {new_mileage}")
    
    return {
        "message": "Kilometraje actualizado exitosamente",
        "vehicle_id": vehicle_id,
        "old_mileage": old_mileage,
        "new_mileage": new_mileage,
        "placa": vehicle.placa
    }

@router.get("/available/")
def get_available_vehicles(
    fecha_inicio: datetime = Query(..., description="Fecha y hora de inicio del viaje"),
    fecha_fin: datetime = Query(..., description="Fecha y hora de fin del viaje"),
    tipo_vehiculo: Optional[VehicleType] = Query(None, description="Tipo de vehículo requerido"),
    capacidad_minima: Optional[int] = Query(None, ge=1, description="Capacidad mínima de pasajeros"),
    db: Session = Depends(get_db)
):
    """Obtiene vehículos disponibles para un período específico"""
    
    # TODO: Implementar lógica para verificar disponibilidad basada en asignaciones
    
    query = db.query(Vehicle).filter(
        Vehicle.activo == True,
        Vehicle.estado == VehicleStatus.DISPONIBLE
    )
    
    if tipo_vehiculo:
        query = query.filter(Vehicle.tipo_vehiculo == tipo_vehiculo)
    
    if capacidad_minima:
        query = query.filter(Vehicle.capacidad_pasajeros >= capacidad_minima)
    
    available_vehicles = query.all()
    
    return {
        "available_vehicles": [VehicleSchema.model_validate(v) for v in available_vehicles],
        "period": {
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        },
        "filters": {
            "tipo_vehiculo": tipo_vehiculo,
            "capacidad_minima": capacidad_minima
        }
    }