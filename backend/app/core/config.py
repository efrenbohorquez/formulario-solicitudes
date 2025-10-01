from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Configuración de la aplicación
    PROJECT_NAME: str = "Sistema de Gestión de Flota - Personería"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Configuración de la base de datos
    DATABASE_URL: str = "sqlite:///./fleet_management.db"
    
    # Configuración de seguridad
    SECRET_KEY: str = "tu-clave-secreta-muy-segura-aqui-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 días
    
    # Configuración CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Configuración de email
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USER: str = ""
    EMAIL_PASSWORD: str = ""
    FROM_EMAIL: str = "sistema@personeria.gov.co"
    
    # Configuración de notificaciones
    ENABLE_NOTIFICATIONS: bool = True
    NOTIFICATION_CHECK_INTERVAL: int = 6  # horas
    
    # Configuración de mantenimiento
    MAINTENANCE_KM_INTERVAL: int = 10000  # km
    MAINTENANCE_ALERT_KM_THRESHOLD: int = 1000  # km
    
    # Configuración de documentos
    DOCUMENT_EXPIRY_WARNING_DAYS: int = 30
    DOCUMENT_CRITICAL_WARNING_DAYS: int = 7
    
    # Configuración de archivos
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: List[str] = [".xlsx", ".xls", ".csv"]
    
    # Configuración de paginación
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instancia global de configuración
settings = Settings()