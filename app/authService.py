
from fastapi import HTTPException, Request,status
from pydantic import BaseModel
from app.database import users_collection
from datetime import datetime
import secrets
import redis
import aioredis
import os

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

#redis_client = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", encoding="utf-8", decode_responses=True)

# Rate Limits
RATE_LIMITS = {"FREEMIUM": 5, "PREMIUM": 50}


redis_client = redis.StrictRedis(host="redis", port=6379, db=0)  # Use "redis" for Docker

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

def authenticate(api_key: str):
    """Check API key in Authorization header."""
    if not api_key:
        raise HTTPException(status_code=401, detail="Falta su API Key")

    user = users_collection.find_one({"api_key": api_key})
    if not user:
        raise HTTPException(status_code=403, detail="API key inválida")

    return user

def rate_limit_middleware(request: Request):
    api_key = request.headers.get("Authorization")
    user = authenticate(api_key)
    
    user_type = user.get("account_type", "FREEMIUM").upper()
    current_minute = datetime.now().strftime("%Y-%m-%d-%H-%M")
    redis_key = f"{api_key}:{current_minute}"
    
    request_count = redis_client.incr(redis_key)
    if request_count == 1:
        redis_client.expire(redis_key, 60)
    
    if request_count > RATE_LIMITS[user_type]:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
