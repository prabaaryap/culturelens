# routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import List # Tambahkan ini untuk response list

from db import database, models
from schemas import schemas
from core.config import settings
from .auth import get_user_by_username

router = APIRouter(tags=["Users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- 1. Fungsi User Biasa (Sudah ada, tidak diubah) ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# --- 2. Fungsi Pengecekan Admin (BARU) ---
def get_current_admin(current_user: models.User = Depends(get_current_user)):
    # Cek apakah kolom role isinya "admin"
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki izin akses (Admin Only)"
        )
    return current_user

# --- Endpoint User Biasa ---
@router.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# --- Endpoint Khusus Admin (BARU) ---
# Endpoint ini akan menampilkan SEMUA user yang terdaftar
@router.get("/users", response_model=List[schemas.User])
def read_all_users(
    db: Session = Depends(database.get_db), 
    current_admin: models.User = Depends(get_current_admin) # Kunci gembok admin dipasang di sini
):
    users = db.query(models.User).all()
    return users