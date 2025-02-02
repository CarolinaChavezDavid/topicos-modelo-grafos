from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from contextlib import asynccontextmanager
from app.authService import register_user, rate_limit_middleware, UserCreate
from app.modelService import load_model, clear_cache, find_similars
from app.logService import log_request, get_memechached_logs, logger
import aioredis
import time

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    load_model() 
    yield
    clear_cache()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}

@app.post("/register/")
def register(user: UserCreate):
    """Create new user and returns its API key."""
    return register_user(user)

@app.post("/similars/{head_id}")
async def get_similars(
    head_id: int,
    request: Request, 
    is_allowed: dict = Depends(rate_limit_middleware),
):
    """Returns the model predictions of the 10 most similars elements"""

    api_key = request.headers.get("Authorization", "UNKNOWN")
    request_start_time = time.time()

    try:
        results = find_similars(head_id)
        model_response_time = time.time()
        request_end_time = time.time()
        log_request(api_key, "/similars/", request_start_time, request_end_time, model_response_time)
        return {"head_id": head_id, "similar_items": results}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/logs/")
def get_logs(request: Request):
    """Returns the logs from a same api key."""
    api_key = request.headers.get("Authorization", "UNKNOWN")
    logger.info(f"logsss api: {api_key}")

    return {"logs": get_memechached_logs(api_key)}
