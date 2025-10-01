from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...database.models import TransportRequest, RequestStatus
from ...schemas.schemas import (
    TransportRequest as TransportRequestSchema,
    TransportRequestCreate,
    TransportRequestUpdate,
    PaginatedResponse
)
from ...services.excel_processor import excel_processor
import logging
from datetime import datetime, date
import tempfile
import os

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
def get_transport_requests(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(20, ge=1, le=100, description="Número de registros a retornar"),
    numero_solicitud: Optional[str] = Query(None, description="Filtrar por número de solicitud"),
    solicitante: Optional[str] = Query(None, description="Filtrar por nombre del solicitante"),
    estado: Optional[RequestStatus] = Query(None, description="Filtrar por estado"),
    fecha_desde: Optional[date] = Query(None, description="Filtrar desde fecha de viaje"),
    fecha_hasta: Optional[date] = Query(None, description="Filtrar hasta fecha de viaje"),
    dependencia: Optional[str] = Query(None, description="Filtrar por dependencia"),
    db: Session = Depends(get_db)
):
    """Obtiene lista de solicitudes de transporte con filtros y paginación"""
    
    query = db.query(TransportRequest)
    
    # Aplicar filtros
    if numero_solicitud:
        query = query.filter(TransportRequest.numero_solicitud.ilike(f"%{numero_solicitud}%"))
    if solicitante:
        query = query.filter(TransportRequest.nombre_solicitante.ilike(f"%{solicitante}%"))
    if estado:
        query = query.filter(TransportRequest.estado == estado)
    if dependencia:
        query = query.filter(TransportRequest.dependencia.ilike(f"%{dependencia}%"))
    if fecha_desde:
        query = query.filter(TransportRequest.fecha_viaje >= fecha_desde)
    if fecha_hasta:
        fecha_hasta_end = datetime.combine(fecha_hasta, datetime.max.time())
        query = query.filter(TransportRequest.fecha_viaje <= fecha_hasta_end)
    
    # Ordenar por fecha de creación descendente
    query = query.order_by(TransportRequest.created_at.desc())
    
    # Obtener total de registros
    total = query.count()
    
    # Aplicar paginación
    requests = query.offset(skip).limit(limit).all()
    
    # Calcular páginas
    pages = (total + limit - 1) // limit
    current_page = (skip // limit) + 1
    
    return PaginatedResponse(
        items=[TransportRequestSchema.model_validate(r) for r in requests],
        total=total,
        page=current_page,
        pages=pages,
        per_page=limit
    )

@router.get("/{request_id}", response_model=TransportRequestSchema)
def get_transport_request(request_id: int, db: Session = Depends(get_db)):
    """Obtiene una solicitud de transporte específica por ID"""
    
    request = db.query(TransportRequest).filter(
        TransportRequest.id == request_id
    ).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud de transporte no encontrada"
        )
    
    return TransportRequestSchema.model_validate(request)

@router.post("/", response_model=TransportRequestSchema, status_code=status.HTTP_201_CREATED)
def create_transport_request(request: TransportRequestCreate, db: Session = Depends(get_db)):
    """Crea una nueva solicitud de transporte"""
    
    # Generar número de solicitud único si no se proporciona
    if not request.numero_solicitud:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        request.numero_solicitud = f"SOL-{timestamp}"
    
    # Verificar que el número de solicitud no exista
    existing_request = db.query(TransportRequest).filter(
        TransportRequest.numero_solicitud == request.numero_solicitud
    ).first()
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una solicitud con este número"
        )
    
    # Validar que la fecha del viaje sea futura
    if request.fecha_viaje <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha del viaje debe ser futura"
        )
    
    # Crear nueva solicitud
    request_data = request.model_dump()
    request_data["fecha_solicitud"] = datetime.now()
    request_data["estado"] = RequestStatus.PENDIENTE
    
    db_request = TransportRequest(**request_data)
    db_request.created_at = datetime.now()
    
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    logger.info(f"Solicitud de transporte creada: {db_request.numero_solicitud} (ID: {db_request.id})")
    
    return TransportRequestSchema.model_validate(db_request)

@router.put("/{request_id}", response_model=TransportRequestSchema)
def update_transport_request(
    request_id: int, 
    request_update: TransportRequestUpdate, 
    db: Session = Depends(get_db)
):
    """Actualiza una solicitud de transporte existente"""
    
    # Buscar solicitud
    db_request = db.query(TransportRequest).filter(
        TransportRequest.id == request_id
    ).first()
    
    if not db_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud de transporte no encontrada"
        )
    
    # No permitir actualización si ya está asignada o completada
    if db_request.estado in [RequestStatus.EN_CURSO, RequestStatus.COMPLETADO]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede modificar una solicitud en curso o completada"
        )
    
    # Validar fecha del viaje si se actualiza
    if request_update.fecha_viaje and request_update.fecha_viaje <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha del viaje debe ser futura"
        )
    
    # Actualizar campos
    update_data = request_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_request, field, value)
    
    db_request.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_request)
    
    logger.info(f"Solicitud de transporte actualizada: {db_request.numero_solicitud} (ID: {db_request.id})")
    
    return TransportRequestSchema.model_validate(db_request)

@router.delete("/{request_id}")
def delete_transport_request(request_id: int, db: Session = Depends(get_db)):
    """Cancela una solicitud de transporte"""
    
    db_request = db.query(TransportRequest).filter(
        TransportRequest.id == request_id
    ).first()
    
    if not db_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud de transporte no encontrada"
        )
    
    # No permitir cancelación si ya está en curso o completada
    if db_request.estado in [RequestStatus.EN_CURSO, RequestStatus.COMPLETADO]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede cancelar una solicitud en curso o completada"
        )
    
    # Marcar como cancelada
    db_request.estado = RequestStatus.CANCELADO
    db_request.updated_at = datetime.now()
    
    db.commit()
    
    logger.info(f"Solicitud de transporte cancelada: {db_request.numero_solicitud} (ID: {db_request.id})")
    
    return {"message": "Solicitud de transporte cancelada exitosamente"}

@router.post("/upload-excel")
async def upload_excel_file(
    file: UploadFile = File(..., description="Archivo Excel con solicitudes de transporte"),
    db: Session = Depends(get_db)
):
    """Sube y procesa un archivo Excel con múltiples solicitudes de transporte"""
    
    # Validar tipo de archivo
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser un Excel (.xlsx o .xls)"
        )
    
    # Validar tamaño del archivo (máximo 10 MB)
    max_size = 10 * 1024 * 1024  # 10 MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo es demasiado grande. Máximo 10 MB"
        )
    
    # Guardar archivo temporalmente
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name
        
        # Procesar archivo Excel
        result = excel_processor.process_excel_file(tmp_file_path, db)
        
        # Limpiar archivo temporal
        os.unlink(tmp_file_path)
        
        return {
            "filename": file.filename,
            "file_size": len(file_content),
            "processing_result": result
        }
        
    except Exception as e:
        # Limpiar archivo temporal en caso de error
        if 'tmp_file_path' in locals():
            try:
                os.unlink(tmp_file_path)
            except:
                pass
        
        logger.error(f"Error procesando archivo Excel: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando archivo: {str(e)}"
        )

@router.get("/excel-template/")
def get_excel_template():
    """Obtiene la estructura del template de Excel para solicitudes de transporte"""
    
    template_info = excel_processor.get_excel_template()
    
    return {
        "template_info": template_info,
        "instructions": [
            "Descargue el template de Excel desde este endpoint",
            "Complete todas las columnas requeridas (marcadas como required: true)",
            "Las fechas deben estar en formato YYYY-MM-DD HH:MM",
            "Los valores de prioridad pueden ser: baja, media, alta, critica",
            "El campo 'requiere_vehiculo_especial' acepta: Si, No, True, False",
            "Guarde el archivo y súbalo usando el endpoint /upload-excel"
        ],
        "download_url": "/api/v1/requests/download-template"
    }

@router.get("/download-template")
async def download_excel_template():
    """Descarga un archivo de template de Excel"""
    
    try:
        import pandas as pd
        from fastapi.responses import StreamingResponse
        import io
        
        # Crear DataFrame con el template
        template_data = excel_processor.get_excel_template()
        
        # Crear DataFrame con las columnas y datos de ejemplo
        columns = [col["name"] for col in template_data["columns"]]
        example_data = template_data["example_data"]
        
        df = pd.DataFrame(example_data, columns=columns)
        
        # Crear archivo Excel en memoria
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Solicitudes')
            
            # Agregar hoja con instrucciones
            instructions_data = {
                'Campo': [col["name"] for col in template_data["columns"]],
                'Requerido': [col["required"] for col in template_data["columns"]],
                'Descripción': [col["description"] for col in template_data["columns"]]
            }
            instructions_df = pd.DataFrame(instructions_data)
            instructions_df.to_excel(writer, index=False, sheet_name='Instrucciones')
        
        excel_buffer.seek(0)
        
        return StreamingResponse(
            io.BytesIO(excel_buffer.getvalue()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": "attachment; filename=template_solicitudes_transporte.xlsx"}
        )
        
    except Exception as e:
        logger.error(f"Error generando template de Excel: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando template: {str(e)}"
        )

@router.get("/pending/")
def get_pending_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    prioridad: Optional[str] = Query(None, description="Filtrar por prioridad"),
    db: Session = Depends(get_db)
):
    """Obtiene solicitudes pendientes de asignación"""
    
    query = db.query(TransportRequest).filter(
        TransportRequest.estado == RequestStatus.PENDIENTE
    )
    
    if prioridad:
        query = query.filter(TransportRequest.prioridad == prioridad)
    
    # Ordenar por prioridad y fecha de viaje
    query = query.order_by(
        TransportRequest.prioridad.desc(),
        TransportRequest.fecha_viaje
    )
    
    total = query.count()
    pending_requests = query.offset(skip).limit(limit).all()
    
    return {
        "pending_requests": [TransportRequestSchema.model_validate(r) for r in pending_requests],
        "total": total,
        "page": (skip // limit) + 1,
        "pages": (total + limit - 1) // limit,
        "summary": {
            "total_pending": total,
            "urgent_requests": db.query(TransportRequest).filter(
                TransportRequest.estado == RequestStatus.PENDIENTE,
                TransportRequest.prioridad.in_(['alta', 'critica'])
            ).count()
        }
    }

@router.get("/statistics/")
def get_requests_statistics(
    fecha_desde: Optional[date] = Query(None, description="Fecha inicio para estadísticas"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha fin para estadísticas"),
    db: Session = Depends(get_db)
):
    """Obtiene estadísticas de las solicitudes de transporte"""
    
    query = db.query(TransportRequest)
    
    if fecha_desde:
        query = query.filter(TransportRequest.fecha_solicitud >= fecha_desde)
    if fecha_hasta:
        fecha_hasta_end = datetime.combine(fecha_hasta, datetime.max.time())
        query = query.filter(TransportRequest.fecha_solicitud <= fecha_hasta_end)
    
    # Estadísticas básicas
    total_requests = query.count()
    
    # Por estado
    stats_by_status = {}
    for status in RequestStatus:
        count = query.filter(TransportRequest.estado == status).count()
        stats_by_status[status.value] = count
    
    # Por prioridad
    stats_by_priority = {}
    from ...database.models import AlertPriority
    for priority in AlertPriority:
        count = query.filter(TransportRequest.prioridad == priority).count()
        stats_by_priority[priority.value] = count
    
    # Por dependencia (top 10)
    from sqlalchemy import func
    top_dependencies = query.filter(
        TransportRequest.dependencia.isnot(None)
    ).with_entities(
        TransportRequest.dependencia,
        func.count(TransportRequest.id).label('count')
    ).group_by(
        TransportRequest.dependencia
    ).order_by(
        func.count(TransportRequest.id).desc()
    ).limit(10).all()
    
    return {
        "period": {
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta
        },
        "total_requests": total_requests,
        "by_status": stats_by_status,
        "by_priority": stats_by_priority,
        "top_dependencies": [
            {"dependencia": dep[0], "count": dep[1]} 
            for dep in top_dependencies
        ]
    }