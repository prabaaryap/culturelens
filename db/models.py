from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base 

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    
    # PERBAIKAN: Tambahkan (255) pada semua String
    name = Column(String(255)) 
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    
    is_active = Column(Boolean, default=True)
    posts = relationship("Post", back_populates="owner")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    
    # PERBAIKAN: Gunakan String(255) untuk caption pendek.
    # Jika Anda ingin teks yang SANGAT panjang (seperti artikel blog), 
    # Anda bisa mengganti String(255) dengan Text
    content = Column(String(255), index=True)
    
    # URL gambar biasanya cukup 255 karakter, tapi jika URL sangat panjang
    # (misal dari Google Storage yang token-nya panjang), amannya pakai String(500) atau Text
    image_url = Column(String(500)) 
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="posts")