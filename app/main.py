from fastapi import FastAPI, HTTPException
from pymemcache.client.base import Client
from pydantic import BaseModel
import app.model_service.inferanceModel
import json
import hashlib

app = FastAPI()
cache = Client(('localhost', 11211))

class User(BaseModel):
    username: str
    password: str
    user_type: str

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@app.post("/register")
def user_registration(user: User):
    existing_user = cache.get(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya esta  registrado")

    hashed_password = hash_password(user.password)

    user_data = {
        "username": user.username,
        "user_type": user.user_type,
        "password": hashed_password
    }

    cache.set(user.username, json.dumps(user_data))
    cache.add("users", user.username)

    return {"message": "El usuario se ha registrado exitosamente"}

@app.get("/users")
def get_all_users():
    user_keys = cache.get("users")
    if not user_keys:
        return {"message": "No se han encontrado usuarios"}

    user_keys = json.loads(user_keys)

    users = []
    for key in user_keys:
        user_data = cache.get(key)
        if user_data:
            users.append(json.loads(user_data))

    return {"users": users}


@app.post("/login")
def login_user(username: str, password: str):
    user_data = cache.get(username)
    if not user_data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user_data = json.loads(user_data)

    hashed_password = hash_password(password)
    if user_data["password"] != hashed_password:
        raise HTTPException(status_code=401, detail="Credenciales invalidas")

    return {"message": "Login exitoso"}

@app.post("/predict/{property_id}/similar")
def login_user(property_id: str):

    return {"message": "Login exitoso"}