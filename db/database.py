import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- JANGAN IMPORT settings DARI config.py UNTUK URL DATABASE ---
# Kita ambil variabel mentah langsung dari sistem (Cloud Run Variables)

DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")
DB_CONNECTION_NAME = os.environ.get("DB_CONNECTION_NAME")

# Cek apakah kita punya Connection Name (Tanda kita ada di Cloud Run)
if DB_CONNECTION_NAME:
    # === JALUR GOOGLE CLOUD (MySQL) ===
    socket_path = f"/cloudsql/{DB_CONNECTION_NAME}"
    
    # Kita RAKIT SENDIRI URL-nya di sini
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@/{DB_NAME}?unix_socket={socket_path}"
    
    # Buat engine
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

else:
    # === JALUR LAPTOP (SQLite) ===
    # Fallback jika coding di laptop
    SQLALCHEMY_DATABASE_URL = "sqlite:///./culturelens_local.db"
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

# --- Setup Standard SQLAlchemy ---
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()