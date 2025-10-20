from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base # 'Base' diimpor dari database.py

class User(Base): # User mewarisi 'Base'
    __tablename__ = "users"
    # ... sisa kode model User ...
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    posts = relationship("Post", back_populates="owner")


class Post(Base): # Post juga mewarisi 'Base'
    __tablename__ = "posts"
    # ... sisa kode model Post ...
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, index=True)
    image_url = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="posts")