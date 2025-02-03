
from fastapi import FastAPI, HTTPException, Request, Depends
import httpx
import os
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")
MODEL_SERVICE_URL = os.getenv("MODEL_SERVICE_URL", "http://model-service:8000")
LOG_SERVICE_URL = os.getenv("LOG_SERVICE_URL", "http://log-service:8000")

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API Gateway esta funcionando!"}

async def check_rate_limit(request: Request):
    """Calls the auth service to check if the request is allowed."""
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/rate-limit-check",
                headers=request.headers,
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Error calling auth service: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="El servicio de autorizacion no esta disponble")
    

async def log_request_to_log_service(api_key: str, endpoint: str, request_start_time: float, request_end_time: float, model_response_time: float):
    """Calls the log service to log the request."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LOG_SERVICE_URL}/log/",
                json={
                    "api_key": api_key,
                    "endpoint": endpoint,
                    "request_start_time": request_start_time,
                    "request_end_time": request_end_time,
                    "model_response_time": model_response_time,
                },
                timeout=5.0,
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as e:
        logger.error(f"Error calling log service: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    
async def log(api_key: str, endpoint: str, request_start_time: float, request_end_time: float, model_response_time: float):
    """Calls the log service to log the request"""
    
    try:
        async with httpx.AsyncClient() as client:
            await client.post(f"{LOG_SERVICE_URL}/log/[")
    
    except httpx.HTTPStatusError as e:
        logger.error(f"Error calling auth service: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="El servicio de autorizacion no esta disponble")
    

@app.post("/register/")
async def register_user(request: Request):
    """Forwards request to the Authentication service"""
    try:
        user_data = await request.json()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/register/",
                json=user_data,
                timeout=30.0
            )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return response.json()

    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="El servicio de autorizacion no esta disponble")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
@app.post("/similars/{head_id}")
async def get_similars(
    head_id: int, 
    request: Request, 
    rate_limit: dict = Depends(check_rate_limit)
    ):
    """Forwards request to Model Service"""
    api_key = request.headers.get("Authorization", "UNKNOWN")
    request_start_time = time.time()

    if not rate_limit.get("allowed", False):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{MODEL_SERVICE_URL}/similars/{head_id}", timeout=30.0)
            response.raise_for_status()
            model_response_time = time.time()
            request_end_time = time.time()
            log_request_to_log_service(api_key, "/similars/", request_start_time, request_end_time, model_response_time)
            return {"head_id": head_id, "similar_items": response}

    except httpx.HTTPStatusError as e:
        logger.error(f"Error calling model service: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/logs/")
async def get_logs(request: Request):
    """Forwards request to Log Service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{LOG_SERVICE_URL}/logs/", headers=request.headers)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return response.json()

    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="El servicio de log no esta disponble")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
   