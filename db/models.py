from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base 

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # Perhatikan semua String punya angka (255)
    name = Column(String(255)) 
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    
    posts = relationship("Post", back_populates="owner")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Untuk konten postingan, kita pakai Text (bisa panjang sekali)
    # Jika ingin pendek, pakai String(255)
    content = Column(Text, index=True) 
    
    # URL gambar kita beri jatah lebih banyak (500)
    image_url = Column(String(500)) 
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="posts")