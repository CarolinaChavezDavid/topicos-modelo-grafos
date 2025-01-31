from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from contextlib import asynccontextmanager
from app.authService import register_user, authenticate, UserCreate
from app.modelService import load_model, clear_cache, find_similars


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    load_model()
    yield
    clear_cache()

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}

@app.post("/register/")
def register(user: UserCreate):
    return register_user(user)

@app.post("/similars/{head_id}")
def register(head_id: int, user: dict = Depends(authenticate)):
    try:
        results = find_similars(head_id)
        return {"user": user, "head_id": head_id, "similar_items": results}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))