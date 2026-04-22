from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
from app.utils.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.vendeur import Vendeur
from app.schemas.user import UserOut, UserCreate, UserRegister, UserBase
from app.utils.security import get_password_hash, create_access_token, SECRET_KEY, ALGORITHM
from jose import JWTError, jwt
from datetime import timedelta

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_active=user.is_active,
        is_admin=user.is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/register", response_model=UserOut)
def register_user(
    payload: UserRegister, 
    db: Session = Depends(get_db)
):
    # Overwrite if exists check
    db_user = db.query(User).filter(User.email == payload.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(payload.password)
    new_user = User(
        email=payload.email,
        hashed_password=hashed_password,
        full_name=payload.full_name,
        role=payload.role,
        phone_number=payload.phone_number,
        is_admin=(payload.role == 'Autorité locale')
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # If Vendeur, populate MYSQL table vendeurs
    if payload.role == 'Vendeur':
        name_parts = payload.full_name.split(" ", 1)
        nom = name_parts[0]
        prenom = name_parts[1] if len(name_parts) > 1 else ""
        
        new_vendeur = Vendeur(
            nom=nom,
            prenom=prenom,
            identifiant_national=payload.identifiant_national or f"NC-{new_user.id}",
            telephone=payload.phone_number,
            emplacement=payload.emplacement or "Non spécifié"
        )
        db.add(new_vendeur)
        db.commit()
        db.refresh(new_vendeur)
        
        # Link User to Vendeur
        new_user.vendeur_id = new_vendeur.id
        db.add(new_user)
        db.commit()
        
    return new_user

@router.get("/check-email")
def check_email(email: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == email).first()
    return {"exists": db_user is not None}

@router.post("/forgot-password")
def forgot_password(email: str = Body(..., embed=True), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Email non trouvé")
    
    # Generate token valid for 15 minutes
    token = create_access_token(data={"sub": email}, expires_delta=timedelta(minutes=15))
    
    # Simulate sending email
    reset_link = f"http://localhost:5173/reset-password?token={token}"
    print("\n" + "="*50)
    print("SIMULATED EMAIL SENT")
    print(f"To: {email}")
    print(f"Reset Link: {reset_link}")
    print("="*50 + "\n")
    
    return {"message": "Lien de réinitialisation envoyé par email (voir console backend)"}

@router.post("/reset-password-with-token")
def reset_password_with_token(
    token: str = Body(...), 
    new_password: str = Body(...), 
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Token invalide")
    except JWTError:
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")
        
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    db_user.hashed_password = get_password_hash(new_password)
    db.commit()
    return {"message": "Mot de passe mis à jour avec succès"}

@router.get("/", response_model=List[UserOut])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.patch("/{user_id}/validate", response_model=UserOut)
def validate_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != 'Autorité Locale':
        raise HTTPException(status_code=403, detail="Permission refusée")
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    db_user.status = "valide"
    db.commit()
    db.refresh(db_user)
    return db_user

@router.patch("/{user_id}/reject", response_model=UserOut)
def reject_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != 'Autorité Locale':
        raise HTTPException(status_code=403, detail="Permission refusée")
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    db_user.status = "rejete"
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != 'Autorité Locale' and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Permission refusée")
    
    # Call stored procedure
    db.execute(
        text("CALL sp_UpdateUser(:id, :name, :phone, :role)"),
        {"id": user_id, "name": payload.full_name, "phone": payload.phone_number, "role": payload.role}
    )
    db.commit()
    
    db_user = db.query(User).filter(User.id == user_id).first()
    return db_user
