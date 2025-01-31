
import secrets
from fastapi import HTTPException, Request, Depends
from pydantic import BaseModel
from app.database import users_collection

# Rate Limits
RATE_LIMITS = {"FREEMIUM": 5, "PREMIUM": 50}

class UserCreate(BaseModel):
    username: str
    account_type: str  # "FREEMIUM" or "PREMIUM"

def generate_api_key():
    """Generate a secure API key."""
    return secrets.token_hex(32)

def register_user(user: UserCreate):
    """Register a new user and return an API key."""
    if user.account_type not in RATE_LIMITS:
        raise HTTPException(status_code=400, detail="Tipo de cuenta inválida.")

    existing_user = users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    api_key = generate_api_key()
    users_collection.insert_one({"username": user.username, "api_key": api_key, "account_type": user.account_type})
    return {"message": "Usuario registrado exitosamente.", "api_key": api_key}

def authenticate(request: Request):
    """Check API key in Authorization header."""
    api_key = request.headers.get("Authorization")
    if not api_key:
        raise HTTPException(status_code=401, detail="Falta su API Key")

    user = users_collection.find_one({"api_key": api_key})
    if not user:
        raise HTTPException(status_code=403, detail="API key inválida")

    return user
