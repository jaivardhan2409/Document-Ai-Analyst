from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
from pydantic import BaseModel
from app.config import settings

class TokenData(BaseModel):
    user_id: Optional[str] = None
    exp: Optional[datetime] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Hash password"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "user_id": user_id,
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def decode_access_token(token: str) -> Optional[str]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("user_id")
        if user_id is None:
            return None
        return user_id
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Authentication routes
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str

@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register new user"""
    from app.models.database import User
    
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.username == request.username) | (User.email == request.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create new user
    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=get_password_hash(request.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create token
    access_token = create_access_token(new_user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email
        )
    }

@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login user"""
    from app.models.database import User
    
    user = db.query(User).filter(User.username == request.username).first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            username=user.username,
            email=user.email
        )
    }

# ==========================================
# Admin Endpoints — View All Users
# ==========================================
import os
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "Jaivardhan2409")

@router.get("/admin/users")
async def list_all_users(secret: str, db: Session = Depends(get_db)):
    """List all registered users (admin only).
    Usage: GET /api/auth/admin/users?secret=<ADMIN_SECRET>
    """
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    from app.models.database import User
    users = db.query(User).all()
    
    return {
        "total_users": len(users),
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
            }
            for u in users
        ]
    }

@router.get("/admin/users/count")
async def user_count(secret: str, db: Session = Depends(get_db)):
    """Get total number of registered users (admin only).
    Usage: GET /api/auth/admin/users/count?secret=<ADMIN_SECRET>
    """
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    from app.models.database import User
    count = db.query(User).count()
    return {"total_users": count}
