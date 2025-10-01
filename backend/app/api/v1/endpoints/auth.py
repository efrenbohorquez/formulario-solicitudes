from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from ...core.database import get_db
from ...core.config import settings
from ...database.models import User, UserRole
from ...schemas.schemas import UserCreate, UserLogin, Token, TokenData, User as UserSchema
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Configuración de autenticación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

# Configuración JWT (se puede mover a config.py)
SECRET_KEY = "tu_clave_secreta_muy_segura_aqui_cambiala_en_produccion"  # TODO: Mover a variables de entorno
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña plana contra su hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token JWT de acceso"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Autentica un usuario con username y password"""
    user = db.query(User).filter(User.username == username, User.activo == True).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Obtiene el usuario actual desde el token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == token_data.username, User.activo == True).first()
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Verifica que el usuario esté activo"""
    if not current_user.activo:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user

def require_role(required_roles: list):
    """Decorator para requerir roles específicos"""
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.rol not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes para esta operación"
            )
        return current_user
    return role_checker

# Endpoints de autenticación

@router.post("/register", response_model=UserSchema)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Registra un nuevo usuario (solo administradores)"""
    
    # Verificar si el username ya existe
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado"
        )
    
    # Verificar si el email ya existe
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        nombre_completo=user_data.nombre_completo,
        password_hash=hashed_password,
        rol=user_data.rol,
        activo=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"Usuario creado: {db_user.username} por {current_user.username}")
    
    return db_user

@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Endpoint para iniciar sesión y obtener token de acceso"""
    
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Actualizar último acceso
    user.ultimo_acceso = datetime.utcnow()
    db.commit()
    
    logger.info(f"Usuario autenticado: {user.username}")
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user
    )

@router.post("/login", response_model=Token)
def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Endpoint alternativo para login con JSON"""
    
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Actualizar último acceso
    user.ultimo_acceso = datetime.utcnow()
    db.commit()
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user
    )

@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Obtiene información del usuario actual"""
    return current_user

@router.put("/change-password")
def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cambia la contraseña del usuario actual"""
    
    # Verificar contraseña actual
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta"
        )
    
    # Validar nueva contraseña (mínimo 8 caracteres)
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nueva contraseña debe tener al menos 8 caracteres"
        )
    
    # Actualizar contraseña
    current_user.password_hash = get_password_hash(new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    logger.info(f"Contraseña cambiada para usuario: {current_user.username}")
    
    return {"message": "Contraseña actualizada correctamente"}

@router.get("/users", response_model=list[UserSchema])
def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Lista todos los usuarios (solo administradores)"""
    
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.put("/users/{user_id}/toggle-status")
def toggle_user_status(
    user_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Activa/desactiva un usuario (solo administradores)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # No permitir desactivar el propio usuario
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propio usuario"
        )
    
    user.activo = not user.activo
    user.updated_at = datetime.utcnow()
    db.commit()
    
    status_text = "activado" if user.activo else "desactivado"
    logger.info(f"Usuario {user.username} {status_text} por {current_user.username}")
    
    return {"message": f"Usuario {status_text} correctamente"}

@router.delete("/logout")
def logout_user(current_user: User = Depends(get_current_active_user)):
    """Cierra sesión del usuario (invalidar token en el frontend)"""
    
    # En una implementación completa, aquí se podría agregar el token a una lista negra
    # Por ahora, solo registramos el evento
    logger.info(f"Usuario desconectado: {current_user.username}")
    
    return {"message": "Sesión cerrada correctamente"}

# Endpoint para verificar salud del sistema de autenticación
@router.get("/health")
def auth_health():
    """Verifica el estado del sistema de autenticación"""
    return {
        "status": "healthy",
        "service": "authentication",
        "timestamp": datetime.utcnow()
    }