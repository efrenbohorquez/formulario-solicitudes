#!/usr/bin/env python3
"""
Script de inicialización del sistema de gestión de flota.
Crea las tablas de la base de datos y un usuario administrador por defecto.
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Agregar el directorio backend al path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Import removed - using bcrypt directly

from app.database.models import Base, User, UserRole
from app.core.config import settings

# Contexto de encriptación para contraseñas - simplificado
import bcrypt

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_database():
    """Crea las tablas de la base de datos"""
    print("🔧 Creando base de datos y tablas...")
    
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    print("✅ Tablas creadas exitosamente")
    return engine

def create_admin_user(engine):
    """Crea un usuario administrador por defecto"""
    print("👤 Creando usuario administrador por defecto...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Verificar si ya existe un admin
        existing_admin = db.query(User).filter(User.username == "admin").first()
        
        if existing_admin:
            print("⚠️  Usuario 'admin' ya existe. Saltando creación...")
            return
        
        # Crear usuario admin
        admin_password = "admin123"
        hashed_password = hash_password(admin_password)
        
        admin_user = User(
            username="admin",
            email="admin@personeria.gov.co",
            nombre_completo="Administrador del Sistema",
            hashed_password=hashed_password,
            rol="admin",
            activo=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print(f"✅ Usuario administrador creado:")
        print(f"   - Usuario: admin")
        print(f"   - Contraseña: {admin_password}")
        print(f"   - Email: admin@personeria.gov.co")
        print(f"   ⚠️  IMPORTANTE: Cambiar la contraseña después del primer login")
        
    except Exception as e:
        print(f"❌ Error creando usuario administrador: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_directories():
    """Crea directorios necesarios para la aplicación"""
    print("📁 Creando directorios necesarios...")
    
    directories = [
        "logs",
        "uploads",
        "uploads/excel",
        "uploads/documents",
        "uploads/images"
    ]
    
    for dir_path in directories:
        os.makedirs(dir_path, exist_ok=True)
        print(f"   ✅ {dir_path}")

def main():
    """Función principal de inicialización"""
    print("🚀 Iniciando configuración del Sistema de Gestión de Flota")
    print("=" * 60)
    
    try:
        # Crear directorios
        create_directories()
        
        # Crear base de datos
        engine = create_database()
        
        # Crear usuario admin
        create_admin_user(engine)
        
        print("=" * 60)
        print("✅ ¡Inicialización completada exitosamente!")
        print()
        print("🏃 Para iniciar el servidor:")
        print("   cd backend")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print()
        print("🌐 La API estará disponible en:")
        print("   - Aplicación: http://localhost:8000")
        print("   - Documentación: http://localhost:8000/docs")
        print("   - ReDoc: http://localhost:8000/redoc")
        print()
        print("🔐 Credenciales por defecto:")
        print("   - Usuario: admin")
        print("   - Contraseña: admin123")
        print("   ⚠️  Cambiar credenciales en primer login")
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()