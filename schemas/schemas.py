from pydantic import BaseModel
from typing import List, Optional

# --- Post Schemas ---
class PostBase(BaseModel):
    content: str

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    owner_id: int
    image_url: str

    class Config:
        from_attributes = True

# --- User Schemas ---
class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    name: str
    password: str

class User(UserBase):
    id: int
    name: str
    is_active: bool
    posts: List[Post] = []

    class Config:
        from_attributes = True

# --- Auth/Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None