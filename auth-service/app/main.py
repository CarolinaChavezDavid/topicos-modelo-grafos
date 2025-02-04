from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel
from app.database import users_collection, redis_client
from datetime import datetime
import secrets
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

class UserCreate(BaseModel):
    username: str
    account_type: str

RATE_LIMITS = {"FREEMIUM": 5, "PREMIUM": 50}

def generate_api_key():
    """Generate a secure API key."""
    return secrets.token_hex(32)

@app.post("/register/")
def register_user(user: UserCreate):
    """Registers a new user"""
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

@app.post("/rate-limit-check")
async def rate_limit_middleware(request: Request):
    api_key = request.headers.get("Authorization")
    user = authenticate(api_key)
    
    user_type = user["account_type"].upper()
    current_minute = datetime.now().strftime("%Y-%m-%d-%H-%M")
    redis_key = f"{api_key}:{current_minute}"
    
    request_count = redis_client.incr(redis_key)
    logger.info(f"Redis count: {request_count}")
    if request_count == 1:
        redis_client.expire(redis_key, 60)
    
    if request_count > RATE_LIMITS[user_type]:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Número de requests excedidos.")

    return {"allowed": True}
