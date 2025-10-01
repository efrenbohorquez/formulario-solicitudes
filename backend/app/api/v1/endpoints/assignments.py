from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...database.models import (
    Assignment, Vehicle, Driver, TransportRequest, 
    VehicleStatus, DriverStatus, RequestStatus
)
from ...schemas.schemas import (
    Assignment as AssignmentSchema,
    AssignmentCreate,
    AssignmentUpdate,
    PaginatedResponse
)
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
def get_assignments(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(20, ge=1, le=100, description="Número de registros a retornar"),
    vehiculo_id: Optional[int] = Query(None, description="Filtrar por vehículo"),
    conductor_id: Optional[int] = Query(None, description="Filtrar por conductor"),
    fecha_desde: Optional[date] = Query(None, description="Filtrar desde fecha"),
    fecha_hasta: Optional[date] = Query(None, description="Filtrar hasta fecha"),
    activa: Optional[bool] = Query(None, description="Filtrar asignaciones activas"),
    db: Session = Depends(get_db)
):
    """Obtiene lista de asignaciones con filtros y paginación"""
    
    query = db.query(Assignment).join(TransportRequest)
    
    # Aplicar filtros
    if vehiculo_id:
        query = query.filter(Assignment.vehiculo_id == vehiculo_id)
    if conductor_id:
        query = query.filter(Assignment.conductor_id == conductor_id)
    if fecha_desde:
        query = query.filter(TransportRequest.fecha_viaje >= fecha_desde)
    if fecha_hasta:
        fecha_hasta_end = datetime.combine(fecha_hasta, datetime.max.time())
        query = query.filter(TransportRequest.fecha_viaje <= fecha_hasta_end)
    if activa is not None:
        if activa:
            # Asignaciones activas: en curso o programadas para hoy/futuro
            query = query.filter(
                TransportRequest.estado.in_([RequestStatus.ASIGNADO, RequestStatus.EN_CURSO]),
                TransportRequest.fecha_viaje >= datetime.now()
            )
        else:
            # Asignaciones completadas o canceladas
            query = query.filter(
                TransportRequest.estado.in_([RequestStatus.COMPLETADO, RequestStatus.CANCELADO])
            )
    
    # Ordenar por fecha de asignación descendente
    query = query.order_by(Assignment.fecha_asignacion.desc())
    
    # Obtener total de registros
    total = query.count()
    
    # Aplicar paginación
    assignments = query.offset(skip).limit(limit).all()
    
    # Calcular páginas
    pages = (total + limit - 1) // limit
    current_page = (skip // limit) + 1
    
    return PaginatedResponse(
        items=[AssignmentSchema.model_validate(a) for a in assignments],
        total=total,
        page=current_page,
        pages=pages,
        per_page=limit
    )

@router.get("/{assignment_id}", response_model=AssignmentSchema)
def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """Obtiene una asignación específica por ID"""
    
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignación no encontrada"
        )
    
    return AssignmentSchema.model_validate(assignment)

@router.post("/", response_model=AssignmentSchema, status_code=status.HTTP_201_CREATED)
def create_assignment(assignment: AssignmentCreate, db: Session = Depends(get_db)):
    """Crea una nueva asignación de vehículo y conductor a una solicitud"""
    
    # Verificar que la solicitud existe y está pendiente
    request = db.query(TransportRequest).filter(
        TransportRequest.id == assignment.solicitud_id,
        TransportRequest.estado == RequestStatus.PENDIENTE
    ).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada o ya asignada"
        )
    
    # Verificar que el vehículo existe y está disponible
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == assignment.vehiculo_id,
        Vehicle.activo == True,
        Vehicle.estado == VehicleStatus.DISPONIBLE
    ).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado o no disponible"
        )
    
    # Verificar que el conductor existe y está disponible
    driver = db.query(Driver).filter(
        Driver.id == assignment.conductor_id,
        Driver.activo == True,
        Driver.estado == DriverStatus.DISPONIBLE,
        Driver.fecha_vencimiento_licencia > date.today()  # Licencia vigente
    ).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conductor no encontrado, no disponible o con licencia vencida"
        )
    
    # Verificar disponibilidad en el período de la solicitud
    conflicting_assignments = check_availability_conflicts(
        db, assignment.vehiculo_id, assignment.conductor_id, 
        request.fecha_viaje, request.fecha_viaje  # Por ahora asumimos que es el mismo día
    )
    
    if conflicting_assignments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El vehículo o conductor no está disponible en el período solicitado"
        )
    
    # Crear nueva asignación
    db_assignment = Assignment(**assignment.model_dump())
    db_assignment.fecha_asignacion = datetime.now()
    db_assignment.created_at = datetime.now()
    
    # Actualizar estados
    request.estado = RequestStatus.ASIGNADO
    vehicle.estado = VehicleStatus.EN_USO
    driver.estado = DriverStatus.EN_SERVICIO
    
    # Actualizar kilometraje inicial si se proporcionó
    if assignment.kilometraje_inicio and assignment.kilometraje_inicio >= vehicle.kilometraje:
        vehicle.kilometraje = assignment.kilometraje_inicio
    else:
        db_assignment.kilometraje_inicio = vehicle.kilometraje
    
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    
    logger.info(f"Asignación creada: Solicitud {request.numero_solicitud} - Vehículo {vehicle.placa} - Conductor {driver.nombre_completo}")
    
    return AssignmentSchema.model_validate(db_assignment)

def check_availability_conflicts(
    db: Session, 
    vehiculo_id: int, 
    conductor_id: int, 
    fecha_inicio: datetime, 
    fecha_fin: datetime
) -> bool:
    """Verifica conflictos de disponibilidad para vehículo y conductor"""
    
    # Buscar asignaciones que se solapan en el tiempo
    conflicting = db.query(Assignment).join(TransportRequest).filter(
        (Assignment.vehiculo_id == vehiculo_id) | (Assignment.conductor_id == conductor_id),
        TransportRequest.estado.in_([RequestStatus.ASIGNADO, RequestStatus.EN_CURSO]),
        # Verificar solapamiento de fechas
        TransportRequest.fecha_viaje <= fecha_fin,
        TransportRequest.fecha_viaje >= fecha_inicio
    ).first()
    
    return conflicting is not None

@router.put("/{assignment_id}", response_model=AssignmentSchema)
def update_assignment(
    assignment_id: int, 
    assignment_update: AssignmentUpdate, 
    db: Session = Depends(get_db)
):
    """Actualiza una asignación existente"""
    
    # Buscar asignación
    db_assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id
    ).first()
    
    if not db_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignación no encontrada"
        )
    
    # Obtener entidades relacionadas
    request = db.query(TransportRequest).filter(
        TransportRequest.id == db_assignment.solicitud_id
    ).first()
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == db_assignment.vehiculo_id
    ).first()
    driver = db.query(Driver).filter(
        Driver.id == db_assignment.conductor_id
    ).first()
    
    # Si se está cambiando vehículo o conductor, verificar disponibilidad
    if (assignment_update.vehiculo_id and assignment_update.vehiculo_id != db_assignment.vehiculo_id) or \
       (assignment_update.conductor_id and assignment_update.conductor_id != db_assignment.conductor_id):
        
        new_vehicle_id = assignment_update.vehiculo_id or db_assignment.vehiculo_id
        new_conductor_id = assignment_update.conductor_id or db_assignment.conductor_id
        
        conflicts = check_availability_conflicts(
            db, new_vehicle_id, new_conductor_id, 
            request.fecha_viaje, request.fecha_viaje
        )
        
        if conflicts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nuevo vehículo o conductor no está disponible"
            )
    
    # Actualizar campos
    update_data = assignment_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_assignment, field, value)
    
    db_assignment.updated_at = datetime.now()
    
    # Manejar finalización de viaje
    if assignment_update.fecha_fin_real and not db_assignment.fecha_fin_real:
        # Viaje completado
        request.estado = RequestStatus.COMPLETADO
        vehicle.estado = VehicleStatus.DISPONIBLE
        driver.estado = DriverStatus.DISPONIBLE
        
        # Actualizar kilometraje final
        if assignment_update.kilometraje_fin and assignment_update.kilometraje_fin > vehicle.kilometraje:
            vehicle.kilometraje = assignment_update.kilometraje_fin
    
    db.commit()
    db.refresh(db_assignment)
    
    logger.info(f"Asignación actualizada: ID {db_assignment.id}")
    
    return AssignmentSchema.model_validate(db_assignment)

@router.delete("/{assignment_id}")
def cancel_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """Cancela una asignación"""
    
    db_assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id
    ).first()
    
    if not db_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignación no encontrada"
        )
    
    # Obtener entidades relacionadas
    request = db.query(TransportRequest).filter(
        TransportRequest.id == db_assignment.solicitud_id
    ).first()
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == db_assignment.vehiculo_id
    ).first()
    driver = db.query(Driver).filter(
        Driver.id == db_assignment.conductor_id
    ).first()
    
    # No permitir cancelación si el viaje ya comenzó
    if db_assignment.fecha_inicio_real:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede cancelar una asignación que ya comenzó"
        )
    
    # Actualizar estados
    request.estado = RequestStatus.CANCELADO
    if vehicle:
        vehicle.estado = VehicleStatus.DISPONIBLE
    if driver:
        driver.estado = DriverStatus.DISPONIBLE
    
    # Eliminar la asignación
    db.delete(db_assignment)
    db.commit()
    
    logger.info(f"Asignación cancelada: ID {assignment_id}")
    
    return {"message": "Asignación cancelada exitosamente"}

@router.post("/{assignment_id}/start-trip")
def start_trip(
    assignment_id: int,
    kilometraje_inicio: Optional[int] = Query(None, description="Kilometraje al iniciar el viaje"),
    db: Session = Depends(get_db)
):
    """Marca el inicio de un viaje asignado"""
    
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignación no encontrada"
        )
    
    # Verificar que no haya iniciado ya
    if assignment.fecha_inicio_real:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El viaje ya fue iniciado"
        )
    
    # Obtener solicitud
    request = db.query(TransportRequest).filter(
        TransportRequest.id == assignment.solicitud_id
    ).first()
    
    # Marcar inicio del viaje
    assignment.fecha_inicio_real = datetime.now()
    if kilometraje_inicio:
        assignment.kilometraje_inicio = kilometraje_inicio
    
    # Actualizar estado de la solicitud
    request.estado = RequestStatus.EN_CURSO
    
    db.commit()
    
    logger.info(f"Viaje iniciado: Asignación {assignment_id}")
    
    return {
        "message": "Viaje iniciado exitosamente",
        "assignment_id": assignment_id,
        "start_time": assignment.fecha_inicio_real,
        "start_mileage": assignment.kilometraje_inicio
    }

@router.post("/{assignment_id}/end-trip")
def end_trip(
    assignment_id: int,
    kilometraje_fin: int = Query(..., description="Kilometraje al finalizar el viaje"),
    observaciones: Optional[str] = Query(None, description="Observaciones del viaje"),
    calificacion: Optional[int] = Query(None, ge=1, le=5, description="Calificación del servicio"),
    db: Session = Depends(get_db)
):
    """Marca la finalización de un viaje"""
    
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignación no encontrada"
        )
    
    # Verificar que el viaje haya iniciado
    if not assignment.fecha_inicio_real:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El viaje debe haber iniciado para poder finalizarlo"
        )
    
    # Verificar que no haya finalizado ya
    if assignment.fecha_fin_real:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El viaje ya fue finalizado"
        )
    
    # Validar kilometraje
    if kilometraje_fin <= (assignment.kilometraje_inicio or 0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El kilometraje final debe ser mayor al inicial"
        )
    
    # Obtener entidades relacionadas
    request = db.query(TransportRequest).filter(
        TransportRequest.id == assignment.solicitud_id
    ).first()
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == assignment.vehiculo_id
    ).first()
    driver = db.query(Driver).filter(
        Driver.id == assignment.conductor_id
    ).first()
    
    # Actualizar asignación
    assignment.fecha_fin_real = datetime.now()
    assignment.kilometraje_fin = kilometraje_fin
    if observaciones:
        assignment.observaciones_conductor = observaciones
    if calificacion:
        assignment.calificacion_servicio = calificacion
    
    # Actualizar estados
    request.estado = RequestStatus.COMPLETADO
    vehicle.estado = VehicleStatus.DISPONIBLE
    vehicle.kilometraje = kilometraje_fin  # Actualizar kilometraje del vehículo
    driver.estado = DriverStatus.DISPONIBLE
    
    db.commit()
    
    # Verificar si necesita mantenimiento por kilometraje
    from ...services.notification_service import notification_service
    notification_service._check_vehicle_maintenance_due(db, vehicle)
    db.commit()
    
    logger.info(f"Viaje finalizado: Asignación {assignment_id} - Km recorridos: {kilometraje_fin - (assignment.kilometraje_inicio or 0)}")
    
    return {
        "message": "Viaje finalizado exitosamente",
        "assignment_id": assignment_id,
        "end_time": assignment.fecha_fin_real,
        "end_mileage": kilometraje_fin,
        "kilometers_traveled": kilometraje_fin - (assignment.kilometraje_inicio or 0),
        "duration_minutes": int((assignment.fecha_fin_real - assignment.fecha_inicio_real).total_seconds() / 60)
    }

@router.get("/active/")
def get_active_assignments(
    vehiculo_id: Optional[int] = Query(None, description="Filtrar por vehículo"),
    conductor_id: Optional[int] = Query(None, description="Filtrar por conductor"),
    db: Session = Depends(get_db)
):
    """Obtiene asignaciones activas (en curso o programadas para hoy)"""
    
    from datetime import timedelta
    
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    query = db.query(Assignment).join(TransportRequest).filter(
        TransportRequest.estado.in_([RequestStatus.ASIGNADO, RequestStatus.EN_CURSO]),
        TransportRequest.fecha_viaje >= today,
        TransportRequest.fecha_viaje < tomorrow
    )
    
    if vehiculo_id:
        query = query.filter(Assignment.vehiculo_id == vehiculo_id)
    if conductor_id:
        query = query.filter(Assignment.conductor_id == conductor_id)
    
    active_assignments = query.order_by(TransportRequest.fecha_viaje).all()
    
    # Agregar información de estado
    assignments_with_status = []
    for assignment in active_assignments:
        assignment_data = AssignmentSchema.model_validate(assignment).model_dump()
        
        # Determinar estado del viaje
        if assignment.fecha_inicio_real:
            if assignment.fecha_fin_real:
                assignment_data["trip_status"] = "completado"
            else:
                assignment_data["trip_status"] = "en_curso"
        else:
            if assignment.solicitud.fecha_viaje <= datetime.now():
                assignment_data["trip_status"] = "retrasado"
            else:
                assignment_data["trip_status"] = "programado"
        
        assignments_with_status.append(assignment_data)
    
    return {
        "active_assignments": assignments_with_status,
        "total": len(assignments_with_status),
        "summary": {
            "programado": len([a for a in assignments_with_status if a["trip_status"] == "programado"]),
            "en_curso": len([a for a in assignments_with_status if a["trip_status"] == "en_curso"]),
            "retrasado": len([a for a in assignments_with_status if a["trip_status"] == "retrasado"]),
            "completado": len([a for a in assignments_with_status if a["trip_status"] == "completado"])
        }
    }