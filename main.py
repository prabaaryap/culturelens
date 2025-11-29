from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import models
from db.database import engine
from routers import auth, users, posts, detection

# 1. Membuat Tabel Database Otomatis (Jika belum ada)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CultureLens API",
    description="API for Balinese sacred objects detection app.",
    version="1.0.0"
)

# 2. MENAMBAHKAN CORS (PENTING!)
# Ini mengizinkan aplikasi HP/Web dari mana saja untuk mengakses API Anda.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # "*" artinya semua orang boleh akses (Bisa diperketat nanti)
    allow_credentials=True,
    allow_methods=["*"],  # Mengizinkan semua method (GET, POST, dll)
    allow_headers=["*"],  # Mengizinkan semua header (termasuk Authorization Token)
)

# 3. Mendaftarkan Router
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(detection.router)

@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Welcome to the CultureLens API!",
        "status": "active",
        "docs_url": "/docs"
    }