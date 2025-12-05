from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Import fungsi upload GCS
from core.gcs import upload_image_to_gcs 

from db import database, models
from schemas import schemas
from .users import get_current_user

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.post("/", response_model=schemas.Post)
def create_post(
    content: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Validasi File (Opsional: Pastikan yang diupload adalah gambar)
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File harus berupa gambar")

    # 2. Upload ke Google Cloud Storage
    try:
        # [BEST PRACTICE] Reset pointer file ke awal untuk mencegah file terupload kosong
        file.file.seek(0)
        
        # Fungsi ini akan mengembalikan URL publik
        public_url = upload_image_to_gcs(file, file.filename, file.content_type)
        
    except Exception as e:
        # Print error ke Logs Server (bisa dilihat di Cloud Run Logs)
        print(f"Error Upload Traceback: {e}") 
        
        # [PERBAIKAN PENTING] 
        # Tampilkan detail error asli {str(e)} ke layar Swagger/Response
        # Ini agar Anda tahu apakah errornya "403 Forbidden" atau "404 Bucket Not Found"
        raise HTTPException(status_code=500, detail=f"DEBUG INFO: {str(e)}")

    # 3. Simpan URL Cloud Storage ke Database
    db_post = models.Post(
        content=content,
        image_url=public_url, 
        owner_id=current_user.id
    )
    
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@router.get("/", response_model=List[schemas.Post])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    posts = db.query(models.Post).offset(skip).limit(limit).all()
    return posts