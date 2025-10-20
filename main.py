from fastapi import FastAPI
from db import models
from db.database import engine
from routers import auth, users, posts, detection
import os

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Create 'uploads' directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

app = FastAPI(
    title="CultureLens API",
    description="API for Balinese sacred objects detection app.",
    version="1.0.0"
)

# Include all the routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(detection.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the CultureLens API!"}