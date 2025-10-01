from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from .config import settings

# Crear engine de SQLAlchemy
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Cambiar a True para debug
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=False  # Cambiar a True para debug
    )

# Crear SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Dependency para obtener la sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para crear las tablas
def create_tables():
    """Crea todas las tablas en la base de datos"""
    Base.metadata.create_all(bind=engine)

# Función para limpiar la base de datos (solo para desarrollo)
def drop_tables():
    """Elimina todas las tablas (solo para desarrollo)"""
    Base.metadata.drop_all(bind=engine)