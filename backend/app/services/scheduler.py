from apscheduler.schedulers.background import BackgroundScheduler
from .notification_service import notification_service
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def setup_scheduler():
    """Configura y inicia el scheduler para tareas automáticas"""
    try:
        # Iniciar el servicio de notificaciones
        notification_service.start_scheduler()
        
        logger.info("Scheduler configurado exitosamente")
        
    except Exception as e:
        logger.error(f"Error configurando scheduler: {e}")

def shutdown_scheduler():
    """Detiene el scheduler"""
    try:
        notification_service.stop_scheduler()
        if scheduler.running:
            scheduler.shutdown()
        logger.info("Scheduler detenido")
    except Exception as e:
        logger.error(f"Error deteniendo scheduler: {e}")