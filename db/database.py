import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 1. Ambil Variabel Lingkungan
# Kita TIDAK LAGI menggunakan settings.DATABASE_URL dari config.py
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")
DB_CONNECTION_NAME = os.environ.get("DB_CONNECTION_NAME")

print(f"DEBUG: Connection Name detected: {DB_CONNECTION_NAME}")

# 2. Tentukan URL Database
if DB_CONNECTION_NAME:
    # === JALUR GOOGLE CLOUD (MySQL) ===
    socket_path = f"/cloudsql/{DB_CONNECTION_NAME}"
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@/{DB_NAME}?unix_socket={socket_path}"
    
    # Engine untuk MySQL
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

else:
    # === JALUR LAPTOP (SQLite) ===
    print("DEBUG: Using Local SQLite")
    SQLALCHEMY_DATABASE_URL = "sqlite:///./culturelens_local.db"
    
    # Engine untuk SQLite
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

# 3. Setup Session & Base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()