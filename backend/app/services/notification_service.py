from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..database.models import Vehicle, MaintenanceAlert, Driver, AlertPriority
from ..database.database import SessionLocal
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from apscheduler.schedulers.background import BackgroundScheduler
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.email_host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
        self.email_port = int(os.getenv("EMAIL_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USER", "")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "sistema@personeria.gov.co")
    
    def start_scheduler(self):
        """Inicia el scheduler de alertas automáticas"""
        # Verificar alertas cada 6 horas
        self.scheduler.add_job(
            func=self.check_maintenance_alerts,
            trigger="interval",
            hours=6,
            id='maintenance_alerts'
        )
        
        # Verificar documentos vencidos diariamente a las 8 AM
        self.scheduler.add_job(
            func=self.check_document_expiration,
            trigger="cron",
            hour=8,
            minute=0,
            id='document_alerts'
        )
        
        self.scheduler.start()
        logger.info("Scheduler de alertas iniciado")
    
    def stop_scheduler(self):
        """Detiene el scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
    
    def check_maintenance_alerts(self):
        """Verifica y crea alertas de mantenimiento automáticamente"""
        db = SessionLocal()
        try:
            vehicles = db.query(Vehicle).filter(Vehicle.activo == True).all()
            
            for vehicle in vehicles:
                self._check_vehicle_maintenance_due(db, vehicle)
                self._check_document_expiration_for_vehicle(db, vehicle)
            
            db.commit()
        except Exception as e:
            logger.error(f"Error verificando alertas de mantenimiento: {e}")
            db.rollback()
        finally:
            db.close()
    
    def _check_vehicle_maintenance_due(self, db: Session, vehicle: Vehicle):
        """Verifica si un vehículo necesita mantenimiento por kilometraje"""
        # Mantenimiento cada 10,000 km (configurable)
        maintenance_interval = 10000
        
        if vehicle.kilometraje and vehicle.kilometraje > 0:
            km_since_last_maintenance = vehicle.kilometraje % maintenance_interval
            km_until_maintenance = maintenance_interval - km_since_last_maintenance
            
            # Alerta cuando falten 1000 km para mantenimiento
            if km_until_maintenance <= 1000:
                existing_alert = db.query(MaintenanceAlert).filter(
                    MaintenanceAlert.vehiculo_id == vehicle.id,
                    MaintenanceAlert.tipo_alerta == "mantenimiento_km",
                    MaintenanceAlert.activa == True
                ).first()
                
                if not existing_alert:
                    priority = AlertPriority.ALTA if km_until_maintenance <= 500 else AlertPriority.MEDIA
                    
                    alert = MaintenanceAlert(
                        vehiculo_id=vehicle.id,
                        tipo_alerta="mantenimiento_km",
                        mensaje=f"Vehículo {vehicle.placa} necesita mantenimiento. Faltan {km_until_maintenance} km.",
                        prioridad=priority,
                        fecha_vencimiento=datetime.now() + timedelta(days=30)
                    )
                    db.add(alert)
    
    def _check_document_expiration_for_vehicle(self, db: Session, vehicle: Vehicle):
        """Verifica documentos próximos a vencer"""
        now = datetime.now().date()
        
        documents = [
            ("soat", vehicle.fecha_soat, "SOAT"),
            ("tecnicomecanica", vehicle.fecha_tecnicomecanica, "Revisión Técnico-Mecánica"), 
            ("seguro", vehicle.fecha_seguro, "Seguro")
        ]
        
        for doc_type, fecha_vencimiento, doc_name in documents:
            if fecha_vencimiento:
                days_until_expiry = (fecha_vencimiento - now).days
                
                if 0 <= days_until_expiry <= 30:  # Vence en los próximos 30 días
                    existing_alert = db.query(MaintenanceAlert).filter(
                        MaintenanceAlert.vehiculo_id == vehicle.id,
                        MaintenanceAlert.tipo_alerta == f"vencimiento_{doc_type}",
                        MaintenanceAlert.activa == True
                    ).first()
                    
                    if not existing_alert:
                        if days_until_expiry <= 7:
                            priority = AlertPriority.CRITICA
                        elif days_until_expiry <= 15:
                            priority = AlertPriority.ALTA
                        else:
                            priority = AlertPriority.MEDIA
                        
                        alert = MaintenanceAlert(
                            vehiculo_id=vehicle.id,
                            tipo_alerta=f"vencimiento_{doc_type}",
                            mensaje=f"{doc_name} del vehículo {vehicle.placa} vence en {days_until_expiry} días.",
                            prioridad=priority,
                            fecha_vencimiento=fecha_vencimiento
                        )
                        db.add(alert)
    
    def check_document_expiration(self):
        """Verifica vencimiento de licencias de conductores"""
        db = SessionLocal()
        try:
            drivers = db.query(Driver).filter(Driver.activo == True).all()
            now = datetime.now().date()
            
            for driver in drivers:
                if driver.fecha_vencimiento_licencia:
                    days_until_expiry = (driver.fecha_vencimiento_licencia - now).days
                    
                    if 0 <= days_until_expiry <= 30:  # Vence en los próximos 30 días
                        if days_until_expiry <= 7:
                            priority = AlertPriority.CRITICA
                        elif days_until_expiry <= 15:
                            priority = AlertPriority.ALTA
                        else:
                            priority = AlertPriority.MEDIA
                        
                        # Enviar notificación por email si está configurado
                        self.send_license_expiration_notification(driver, days_until_expiry)
            
            db.commit()
        except Exception as e:
            logger.error(f"Error verificando vencimiento de documentos: {e}")
            db.rollback()
        finally:
            db.close()
    
    def send_email_notification(self, to_email: str, subject: str, message: str):
        """Envía notificación por email"""
        try:
            if not self.email_user or not self.email_password:
                logger.warning("Credenciales de email no configuradas")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'html'))
            
            server = smtplib.SMTP(self.email_host, self.email_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.from_email, to_email, text)
            server.quit()
            
            logger.info(f"Email enviado a {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return False
    
    def send_license_expiration_notification(self, driver: Driver, days_until_expiry: int):
        """Envía notificación de vencimiento de licencia"""
        if driver.email:
            subject = f"Alerta: Vencimiento de Licencia - {driver.nombre_completo}"
            message = f"""
            <html>
            <body>
                <h2>Alerta de Vencimiento de Licencia</h2>
                <p><strong>Conductor:</strong> {driver.nombre_completo}</p>
                <p><strong>Cédula:</strong> {driver.cedula}</p>
                <p><strong>Licencia:</strong> {driver.numero_licencia}</p>
                <p><strong>Categoría:</strong> {driver.categoria_licencia}</p>
                <p><strong>Días hasta vencimiento:</strong> <span style="color: red; font-weight: bold;">{days_until_expiry}</span></p>
                
                <p>Por favor, proceda con la renovación correspondiente.</p>
                
                <p><em>Sistema de Gestión de Flota - Personería</em></p>
            </body>
            </html>
            """
            self.send_email_notification(driver.email, subject, message)
    
    def get_active_alerts(self, db: Session) -> List[MaintenanceAlert]:
        """Obtiene todas las alertas activas ordenadas por prioridad"""
        return db.query(MaintenanceAlert).filter(
            MaintenanceAlert.activa == True
        ).order_by(
            MaintenanceAlert.prioridad.desc(),
            MaintenanceAlert.fecha_creacion.desc()
        ).all()
    
    def mark_alert_as_read(self, db: Session, alert_id: int):
        """Marca una alerta como leída"""
        alert = db.query(MaintenanceAlert).filter(MaintenanceAlert.id == alert_id).first()
        if alert:
            alert.vista = True
            db.commit()
    
    def dismiss_alert(self, db: Session, alert_id: int):
        """Descarta/desactiva una alerta"""
        alert = db.query(MaintenanceAlert).filter(MaintenanceAlert.id == alert_id).first()
        if alert:
            alert.activa = False
            db.commit()

# Instancia global del servicio de notificaciones
notification_service = NotificationService()