# routers/auth.py (Hanya bagian register yang perlu diperhatikan)

# ... (import dan kode lain tetap sama) ...

@router.post("/auth/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = security.get_password_hash(user.password)
    
    new_user = models.User(
        email=user.email,
        username=user.username,
        name=user.name,
        hashed_password=hashed_password,
        role="user" # Pastikan user baru selalu jadi 'user' biasa
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ... (kode login tetap sama) ...