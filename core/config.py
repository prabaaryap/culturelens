from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Kita buat ini Optional (boleh kosong) karena di Cloud Run
    # kita merakit URL-nya secara manual di file database.py
    DATABASE_URL: Optional[str] = None
    
    # Tiga ini TETAP WAJIB karena untuk keamanan Login
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"

settings = Settings()