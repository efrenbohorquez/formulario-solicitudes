from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...database.models import Driver, DriverStatus
from ...schemas.schemas import (
    Driver as DriverSchema,
    DriverCreate,
    DriverUpdate,
    PaginatedResponse
)
import logging
from datetime import datetime, date, timedelta

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
def get_drivers(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(20, ge=1, le=100, description="Número de registros a retornar"),
    cedula: Optional[str] = Query(None, description="Filtrar por cédula"),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre"),
    estado: Optional[DriverStatus] = Query(None, description="Filtrar por estado"),
    categoria_licencia: Optional[str] = Query(None, description="Filtrar por categoría de licencia"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    licencia_vigente: Optional[bool] = Query(None, description="Filtrar por licencia vigente"),
    db: Session = Depends(get_db)
):
    """Obtiene lista de conductores con filtros y paginación"""
    
    query = db.query(Driver)
    
    # Aplicar filtros
    if cedula:
        query = query.filter(Driver.cedula.ilike(f"%{cedula}%"))
    if nombre:
        query = query.filter(Driver.nombre_completo.ilike(f"%{nombre}%"))
    if estado:
        query = query.filter(Driver.estado == estado)
    if categoria_licencia:
        query = query.filter(Driver.categoria_licencia.ilike(f"%{categoria_licencia}%"))
    if activo is not None:
        query = query.filter(Driver.activo == activo)
    if licencia_vigente is not None:
        today = date.today()
        if licencia_vigente:
            query = query.filter(Driver.fecha_vencimiento_licencia > today)
        else:
            query = query.filter(Driver.fecha_vencimiento_licencia <= today)
    
    # Obtener total de registros
    total = query.count()
    
    # Aplicar paginación
    drivers = query.offset(skip).limit(limit).all()
    
    # Calcular páginas
    pages = (total + limit - 1) // limit
    current_page = (skip // limit) + 1
    
    return PaginatedResponse(
        items=[DriverSchema.model_validate(d) for d in drivers],
        total=total,
        page=current_page,
        pages=pages,
        per_page=limit
    )

@router.get("/{driver_id}", response_model=DriverSchema)
def get_driver(driver_id: int, db: Session = Depends(get_db)):
    """Obtiene un conductor específico por ID"""
    
    driver = db.query(Driver).filter(
        Driver.id == driver_id,
        Driver.activo == True
    ).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conductor no encontrado"
        )
    
    return DriverSchema.model_validate(driver)

@router.post("/", response_model=DriverSchema, status_code=status.HTTP_201_CREATED)
def create_driver(driver: DriverCreate, db: Session = Depends(get_db)):
    """Crea un nuevo conductor"""
    
    # Verificar que la cédula no exista
    existing_driver = db.query(Driver).filter(Driver.cedula == driver.cedula).first()
    if existing_driver:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un conductor con esta cédula"
        )
    
    # Verificar que el número de licencia no exista
    existing_license = db.query(Driver).filter(Driver.numero_licencia == driver.numero_licencia).first()
    if existing_license:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un conductor con este número de licencia"
        )
    
    # Validar que la licencia no esté vencida
    if driver.fecha_vencimiento_licencia <= date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de vencimiento de la licencia debe ser futura"
        )
    
    # Crear nuevo conductor
    db_driver = Driver(**driver.model_dump())
    db_driver.created_at = datetime.now()
    
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    
    logger.info(f"Conductor creado: {db_driver.nombre_completo} - {db_driver.cedula} (ID: {db_driver.id})")
    
    return DriverSchema.model_validate(db_driver)

@router.put("/{driver_id}", response_model=DriverSchema)
def update_driver(
    driver_id: int, 
    driver_update: DriverUpdate, 
    db: Session = Depends(get_db)
):
    """Actualiza un conductor existente"""
    
    # Buscar conductor
    db_driver = db.query(Driver).filter(
        Driver.id == driver_id,
        Driver.activo == True
    ).first()
    
    if not db_driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conductor no encontrado"
        )
    
    # Si se actualiza la cédula, verificar que no exista
    if driver_update.cedula and driver_update.cedula != db_driver.cedula:
        existing_driver = db.query(Driver).filter(
            Driver.cedula == driver_update.cedula,
            Driver.id != driver_id
        ).first()
        if existing_driver:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un conductor con esta cédula"
            )
    
    # Si se actualiza el número de licencia, verificar que no exista
    if driver_update.numero_licencia and driver_update.numero_licencia != db_driver.numero_licencia:
        existing_license = db.query(Driver).filter(
            Driver.numero_licencia == driver_update.numero_licencia,
            Driver.id != driver_id
        ).first()
        if existing_license:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un conductor con este número de licencia"
            )
    
    # Validar fecha de vencimiento de licencia si se actualiza
    if driver_update.fecha_vencimiento_licencia and driver_update.fecha_vencimiento_licencia <= date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de vencimiento de la licencia debe ser futura"
        )
    
    # Actualizar campos
    update_data = driver_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_driver, field, value)
    
    db_driver.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_driver)
    
    logger.info(f"Conductor actualizado: {db_driver.nombre_completo} - {db_driver.cedula} (ID: {db_driver.id})")
    
    return DriverSchema.model_validate(db_driver)

@router.delete("/{driver_id}")
def delete_driver(driver_id: int, db: Session = Depends(get_db)):
    """Elimina (desactiva) un conductor"""
    
    db_driver = db.query(Driver).filter(
        Driver.id == driver_id,
        Driver.activo == True
    ).first()
    
    if not db_driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conductor no encontrado"
        )
    
    # Verificar si tiene asignaciones activas
    # TODO: Implementar verificación de asignaciones activas
    
    # Soft delete - marcar como inactivo
    db_driver.activo = False
    db_driver.updated_at = datetime.now()
    
    db.commit()
    
    logger.info(f"Conductor eliminado: {db_driver.nombre_completo} - {db_driver.cedula} (ID: {db_driver.id})")
    
    return {"message": "Conductor eliminado exitosamente"}

@router.get("/{driver_id}/assignments")
def get_driver_assignments(
    driver_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    fecha_inicio: Optional[datetime] = Query(None, description="Filtrar desde fecha"),
    fecha_fin: Optional[datetime] = Query(None, description="Filtrar hasta fecha"),
    db: Session = Depends(get_db)
):
    """Obtiene el historial de asignaciones de un conductor"""
    
    # Verificar que el conductor existe
    driver = db.query(Driver).filter(
        Driver.id == driver_id,
        Driver.activo == True
    ).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conductor no encontrado"
        )
    
    # Obtener asignaciones
    from ...database.models import Assignment
    
    assignments_query = db.query(Assignment).filter(
        Assignment.conductor_id == driver_id
    )
    
    # Aplicar filtros de fecha
    if fecha_inicio:
        assignments_query = assignments_query.filter(Assignment.fecha_asignacion >= fecha_inicio)
    if fecha_fin:
        assignments_query = assignments_query.filter(Assignment.fecha_asignacion <= fecha_fin)
    
    assignments_query = assignments_query.order_by(Assignment.fecha_asignacion.desc())
    
    total = assignments_query.count()
    assignments = assignments_query.offset(skip).limit(limit).all()
    
    return {
        "driver": DriverSchema.model_validate(driver),
        "assignments": assignments,
        "total": total,
        "page": (skip // limit) + 1,
        "pages": (total + limit - 1) // limit
    }

@router.get("/available/")
def get_available_drivers(
    fecha_inicio: datetime = Query(..., description="Fecha y hora de inicio del servicio"),
    fecha_fin: datetime = Query(..., description="Fecha y hora de fin del servicio"),
    categoria_licencia: Optional[str] = Query(None, description="Categoría de licencia requerida"),
    anos_experiencia_min: Optional[int] = Query(None, ge=0, description="Años mínimos de experiencia"),
    db: Session = Depends(get_db)
):
    """Obtiene conductores disponibles para un período específico"""
    
    # Filtros base
    query = db.query(Driver).filter(
        Driver.activo == True,
        Driver.estado == DriverStatus.DISPONIBLE,
        Driver.fecha_vencimiento_licencia > date.today()  # Licencia vigente
    )
    
    # Filtros opcionales
    if categoria_licencia:
        query = query.filter(Driver.categoria_licencia.ilike(f"%{categoria_licencia}%"))
    
    if anos_experiencia_min:
        query = query.filter(Driver.años_experiencia >= anos_experiencia_min)
    
    # TODO: Implementar verificación de disponibilidad basada en asignaciones del período
    
    available_drivers = query.all()
    
    # Verificar alertas de licencias próximas a vencer
    drivers_with_alerts = []
    for driver in available_drivers:
        days_to_expire = (driver.fecha_vencimiento_licencia - date.today()).days
        driver_data = DriverSchema.model_validate(driver).model_dump()
        driver_data["days_until_license_expiry"] = days_to_expire
        driver_data["license_alert"] = days_to_expire <= 30
        drivers_with_alerts.append(driver_data)
    
    return {
        "available_drivers": drivers_with_alerts,
        "period": {
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        },
        "filters": {
            "categoria_licencia": categoria_licencia,
            "anos_experiencia_min": anos_experiencia_min
        },
        "summary": {
            "total_available": len(available_drivers),
            "with_license_alerts": len([d for d in drivers_with_alerts if d["license_alert"]])
        }
    }

@router.get("/license-expiry-alerts/")
def get_license_expiry_alerts(
    days_ahead: int = Query(30, ge=1, le=365, description="Días hacia adelante para verificar vencimientos"),
    db: Session = Depends(get_db)
):
    """Obtiene conductores con licencias próximas a vencer"""
    
    future_date = date.today() + timedelta(days=days_ahead)
    
    drivers_expiring = db.query(Driver).filter(
        Driver.activo == True,
        Driver.fecha_vencimiento_licencia <= future_date,
        Driver.fecha_vencimiento_licencia > date.today()
    ).order_by(Driver.fecha_vencimiento_licencia).all()
    
    alerts = []
    for driver in drivers_expiring:
        days_to_expire = (driver.fecha_vencimiento_licencia - date.today()).days
        
        if days_to_expire <= 7:
            priority = "critica"
        elif days_to_expire <= 15:
            priority = "alta"
        else:
            priority = "media"
        
        alerts.append({
            "driver": DriverSchema.model_validate(driver),
            "days_until_expiry": days_to_expire,
            "expiry_date": driver.fecha_vencimiento_licencia,
            "priority": priority
        })
    
    return {
        "alerts": alerts,
        "total_alerts": len(alerts),
        "summary": {
            "critical": len([a for a in alerts if a["priority"] == "critica"]),
            "high": len([a for a in alerts if a["priority"] == "alta"]),
            "medium": len([a for a in alerts if a["priority"] == "media"])
        },
        "days_ahead": days_ahead
    }

@router.post("/{driver_id}/change-status")
def change_driver_status(
    driver_id: int,
    new_status: DriverStatus = Query(..., description="Nuevo estado del conductor"),
    reason: Optional[str] = Query(None, description="Razón del cambio de estado"),
    db: Session = Depends(get_db)
):
    """Cambia el estado de un conductor"""
    
    # Buscar conductor
    driver = db.query(Driver).filter(
        Driver.id == driver_id,
        Driver.activo == True
    ).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conductor no encontrado"
        )
    
    old_status = driver.estado
    driver.estado = new_status
    driver.updated_at = datetime.now()
    
    # TODO: Agregar log de cambio de estado
    
    db.commit()
    
    logger.info(f"Estado del conductor {driver.nombre_completo} cambiado de {old_status} a {new_status}")
    
    return {
        "message": "Estado del conductor actualizado exitosamente",
        "driver_id": driver_id,
        "old_status": old_status,
        "new_status": new_status,
        "reason": reason,
        "timestamp": datetime.now()
    }