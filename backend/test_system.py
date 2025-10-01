#!/usr/bin/env python3
"""
Test básico para verificar las importaciones del sistema
"""

import sys
import os
from pathlib import Path

# Agregar el directorio backend al path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

def test_imports():
    """Prueba todas las importaciones principales"""
    print("🧪 Probando importaciones...")
    
    try:
        print("  ✓ Importando configuración...")
        from app.core.config import settings
        
        print("  ✓ Importando database...")
        from app.core.database import get_db, engine
        
        print("  ✓ Importando modelos...")
        from app.database.models import Vehicle, Driver, User
        
        print("  ✓ Importando schemas...")
        from app.schemas.schemas import VehicleCreate, DriverCreate
        
        print("✅ Todas las importaciones principales funcionan correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en importaciones: {e}")
        return False

def test_database():
    """Prueba la conexión a la base de datos"""
    print("🗄️ Probando conexión a base de datos...")
    
    try:
        from app.core.database import engine
        from app.database.models import Base
        
        # Verificar conexión
        with engine.connect() as conn:
            print("  ✓ Conexión a base de datos exitosa")
            
        print("✅ Base de datos funcional!")
        return True
        
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del sistema...")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    # Test de importaciones
    if test_imports():
        tests_passed += 1
    
    print()
    
    # Test de base de datos
    if test_database():
        tests_passed += 1
    
    print("=" * 50)
    print(f"📊 Resultado: {tests_passed}/{total_tests} pruebas exitosas")
    
    if tests_passed == total_tests:
        print("✅ ¡Sistema listo para funcionar!")
        return 0
    else:
        print("❌ Hay errores que necesitan ser corregidos")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)