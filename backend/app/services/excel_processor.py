import pandas as pd
import openpyxl
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
import logging
from sqlalchemy.orm import Session
from ..database.models import TransportRequest, RequestStatus, AlertPriority
from ..schemas.schemas import TransportRequestCreate
import re
from pathlib import Path

logger = logging.getLogger(__name__)

class ExcelProcessorService:
    """Servicio para procesar archivos Excel con solicitudes de transporte"""
    
    def __init__(self):
        self.required_columns = [
            'nombre_solicitante', 'fecha_viaje', 'origen', 'destino'
        ]
        self.optional_columns = [
            'dependencia', 'telefono_contacto', 'email_contacto', 
            'proposito_viaje', 'numero_pasajeros', 'prioridad',
            'observaciones', 'requiere_vehiculo_especial'
        ]
    
    def validate_excel_file(self, file_path: str) -> Tuple[bool, str]:
        """Valida que el archivo Excel tenga el formato correcto"""
        try:
            if not Path(file_path).exists():
                return False, "El archivo no existe"
            
            # Verificar extensión
            if not file_path.lower().endswith(('.xlsx', '.xls')):
                return False, "El archivo debe ser un Excel (.xlsx o .xls)"
            
            # Intentar leer el archivo
            df = pd.read_excel(file_path)
            
            if df.empty:
                return False, "El archivo está vacío"
            
            # Verificar columnas requeridas
            missing_columns = []
            df_columns = [col.lower().replace(' ', '_') for col in df.columns]
            
            for required_col in self.required_columns:
                if required_col not in df_columns:
                    missing_columns.append(required_col)
            
            if missing_columns:
                return False, f"Faltan las siguientes columnas: {', '.join(missing_columns)}"
            
            return True, "Archivo válido"
            
        except Exception as e:
            logger.error(f"Error validando archivo Excel: {e}")
            return False, f"Error leyendo el archivo: {str(e)}"
    
    def process_excel_file(self, file_path: str, db: Session) -> Dict:
        """Procesa un archivo Excel y crea las solicitudes de transporte"""
        try:
            # Validar archivo
            is_valid, message = self.validate_excel_file(file_path)
            if not is_valid:
                return {
                    "success": False,
                    "message": message,
                    "processed": 0,
                    "errors": []
                }
            
            # Leer archivo Excel
            df = pd.read_excel(file_path)
            
            # Normalizar nombres de columnas
            df.columns = [col.lower().replace(' ', '_').replace('-', '_') for col in df.columns]
            
            processed_count = 0
            errors = []
            created_requests = []
            
            for index, row in df.iterrows():
                try:
                    # Crear solicitud desde la fila
                    request_data = self._create_request_from_row(row, index + 2)  # +2 porque Excel empieza en 1 y header es 1
                    
                    if request_data:
                        # Verificar si ya existe una solicitud similar
                        existing = self._find_similar_request(db, request_data)
                        
                        if not existing:
                            # Crear nueva solicitud
                            new_request = TransportRequest(**request_data)
                            db.add(new_request)
                            db.flush()  # Para obtener el ID
                            
                            created_requests.append({
                                "id": new_request.id,
                                "numero_solicitud": new_request.numero_solicitud,
                                "solicitante": new_request.nombre_solicitante,
                                "fecha_viaje": new_request.fecha_viaje.strftime("%Y-%m-%d %H:%M")
                            })
                            processed_count += 1
                        else:
                            errors.append({
                                "fila": index + 2,
                                "error": f"Solicitud similar ya existe (ID: {existing.id})"
                            })
                
                except Exception as e:
                    errors.append({
                        "fila": index + 2,
                        "error": str(e)
                    })
                    logger.error(f"Error procesando fila {index + 2}: {e}")
            
            # Confirmar cambios si todo salió bien
            if processed_count > 0:
                db.commit()
            else:
                db.rollback()
            
            return {
                "success": True,
                "message": f"Procesamiento completado. {processed_count} solicitudes creadas.",
                "processed": processed_count,
                "errors": errors,
                "created_requests": created_requests
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error procesando archivo Excel: {e}")
            return {
                "success": False,
                "message": f"Error procesando archivo: {str(e)}",
                "processed": 0,
                "errors": [{"fila": "General", "error": str(e)}]
            }
    
    def _create_request_from_row(self, row: pd.Series, row_number: int) -> Optional[Dict]:
        """Crea un diccionario de datos de solicitud desde una fila de Excel"""
        try:
            # Campos obligatorios
            nombre_solicitante = self._clean_string(row.get('nombre_solicitante'))
            if not nombre_solicitante:
                raise ValueError("Nombre del solicitante es obligatorio")
            
            fecha_viaje = self._parse_datetime(row.get('fecha_viaje'))
            if not fecha_viaje:
                raise ValueError("Fecha del viaje es obligatoria y debe ser válida")
            
            origen = self._clean_string(row.get('origen'))
            if not origen:
                raise ValueError("Origen es obligatorio")
            
            destino = self._clean_string(row.get('destino'))
            if not destino:
                raise ValueError("Destino es obligatorio")
            
            # Generar número de solicitud único
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            numero_solicitud = f"SOL-{timestamp}-{row_number}"
            
            # Crear diccionario base
            request_data = {
                "numero_solicitud": numero_solicitud,
                "nombre_solicitante": nombre_solicitante,
                "fecha_solicitud": datetime.now(),
                "fecha_viaje": fecha_viaje,
                "origen": origen,
                "destino": destino,
                "estado": RequestStatus.PENDIENTE
            }
            
            # Campos opcionales
            if pd.notna(row.get('dependencia')):
                request_data["dependencia"] = self._clean_string(row.get('dependencia'))
            
            if pd.notna(row.get('telefono_contacto')):
                request_data["telefono_contacto"] = self._clean_string(row.get('telefono_contacto'))
            
            if pd.notna(row.get('email_contacto')):
                email = self._clean_string(row.get('email_contacto'))
                if email and self._validate_email(email):
                    request_data["email_contacto"] = email
            
            if pd.notna(row.get('proposito_viaje')):
                request_data["proposito_viaje"] = self._clean_string(row.get('proposito_viaje'))
            
            if pd.notna(row.get('numero_pasajeros')):
                try:
                    pasajeros = int(row.get('numero_pasajeros', 1))
                    request_data["numero_pasajeros"] = max(1, pasajeros)
                except (ValueError, TypeError):
                    request_data["numero_pasajeros"] = 1
            
            if pd.notna(row.get('prioridad')):
                prioridad_str = self._clean_string(row.get('prioridad')).lower()
                prioridad_map = {
                    'baja': AlertPriority.BAJA,
                    'media': AlertPriority.MEDIA,
                    'alta': AlertPriority.ALTA,
                    'critica': AlertPriority.CRITICA,
                    'crítica': AlertPriority.CRITICA
                }
                request_data["prioridad"] = prioridad_map.get(prioridad_str, AlertPriority.MEDIA)
            
            if pd.notna(row.get('observaciones')):
                request_data["observaciones"] = self._clean_string(row.get('observaciones'))
            
            if pd.notna(row.get('requiere_vehiculo_especial')):
                especial = str(row.get('requiere_vehiculo_especial')).lower()
                request_data["requiere_vehiculo_especial"] = especial in ['si', 'sí', 'yes', 'true', '1']
            
            return request_data
            
        except Exception as e:
            raise ValueError(f"Error en fila {row_number}: {str(e)}")
    
    def _clean_string(self, value) -> Optional[str]:
        """Limpia y normaliza strings"""
        if pd.isna(value):
            return None
        return str(value).strip()
    
    def _parse_datetime(self, value) -> Optional[datetime]:
        """Parsea una fecha/hora desde Excel"""
        if pd.isna(value):
            return None
        
        try:
            # Si ya es datetime
            if isinstance(value, datetime):
                return value
            
            # Si es date, convertir a datetime
            if isinstance(value, date):
                return datetime.combine(value, datetime.min.time())
            
            # Si es string, intentar parsear
            if isinstance(value, str):
                # Formatos comunes
                formats = [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d %H:%M",
                    "%Y-%m-%d",
                    "%d/%m/%Y %H:%M:%S",
                    "%d/%m/%Y %H:%M",
                    "%d/%m/%Y",
                    "%d-%m-%Y %H:%M:%S",
                    "%d-%m-%Y %H:%M",
                    "%d-%m-%Y"
                ]
                
                for fmt in formats:
                    try:
                        return datetime.strptime(str(value).strip(), fmt)
                    except ValueError:
                        continue
            
            # Si es timestamp de pandas
            if hasattr(value, 'to_pydatetime'):
                return value.to_pydatetime()
            
            return None
            
        except Exception:
            return None
    
    def _validate_email(self, email: str) -> bool:
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _find_similar_request(self, db: Session, request_data: Dict) -> Optional[TransportRequest]:
        """Busca solicitudes similares para evitar duplicados"""
        # Buscar por solicitante, fecha y destino similar
        similar = db.query(TransportRequest).filter(
            TransportRequest.nombre_solicitante == request_data["nombre_solicitante"],
            TransportRequest.fecha_viaje == request_data["fecha_viaje"],
            TransportRequest.destino == request_data["destino"]
        ).first()
        
        return similar
    
    def get_excel_template(self) -> Dict:
        """Retorna la estructura del template de Excel"""
        return {
            "columns": [
                {"name": "nombre_solicitante", "required": True, "description": "Nombre completo del solicitante"},
                {"name": "dependencia", "required": False, "description": "Dependencia o área de trabajo"},
                {"name": "telefono_contacto", "required": False, "description": "Teléfono de contacto"},
                {"name": "email_contacto", "required": False, "description": "Email de contacto"},
                {"name": "fecha_viaje", "required": True, "description": "Fecha y hora del viaje (YYYY-MM-DD HH:MM)"},
                {"name": "origen", "required": True, "description": "Lugar de origen del viaje"},
                {"name": "destino", "required": True, "description": "Lugar de destino del viaje"},
                {"name": "proposito_viaje", "required": False, "description": "Propósito o motivo del viaje"},
                {"name": "numero_pasajeros", "required": False, "description": "Número de pasajeros (default: 1)"},
                {"name": "prioridad", "required": False, "description": "Prioridad: baja, media, alta, critica"},
                {"name": "observaciones", "required": False, "description": "Observaciones adicionales"},
                {"name": "requiere_vehiculo_especial", "required": False, "description": "Si/No - Requiere vehículo especial"}
            ],
            "example_data": [
                {
                    "nombre_solicitante": "Juan Pérez",
                    "dependencia": "Oficina Jurídica",
                    "telefono_contacto": "3001234567",
                    "email_contacto": "juan.perez@personeria.gov.co",
                    "fecha_viaje": "2024-01-15 09:00",
                    "origen": "Personería Municipal",
                    "destino": "Tribunal Administrativo",
                    "proposito_viaje": "Audiencia judicial",
                    "numero_pasajeros": "2",
                    "prioridad": "alta",
                    "observaciones": "Llevar documentos del caso",
                    "requiere_vehiculo_especial": "No"
                }
            ]
        }

# Instancia global del servicio
excel_processor = ExcelProcessorService()