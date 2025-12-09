import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Ambil variabel lingkungan (Environment Variables)
# Nanti kita setting ini di Google Cloud Run Console
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME") # Contoh: project-id:region:instance-id

# 2. Logika Pemilihan Database
if INSTANCE_CONNECTION_NAME:
    # --- JIKA DI CLOUD RUN (Pakai MySQL via Unix Socket) ---
    # Cloud Run terhubung ke SQL lewat "Socket" (seperti kabel langsung), bukan IP Address.
    socket_path = f"/cloudsql/{INSTANCE_CONNECTION_NAME}"
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@/{DB_NAME}?unix_socket={socket_path}"
    
    # Engine untuk MySQL
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
    )
else:
    # --- JIKA DI LAPTOP (Pakai SQLite) ---
    SQLALCHEMY_DATABASE_URL = "sqlite:///./culturelens_local.db"
    
    # Engine untuk SQLite (butuh check_same_thread=False)
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency standard
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()