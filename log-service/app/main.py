from fastapi import FastAPI, Request
from datetime import datetime
from pydantic import BaseModel
import logging
import json
import time
from app.database import memcached_client

app = FastAPI()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class LogRequest(BaseModel):
    api_key: str
    endpoint: str
    request_start_time: float
    request_end_time: float
    model_response_time: float

@app.post("/log/")
def log_request(log_data: LogRequest):
    """Log user request to Memcached."""
    processing_time = log_data.model_response_time - log_data.request_start_time
    total_time = log_data.request_end_time - log_data.request_start_time

    log_entry = {
        "api_key": log_data.api_key,
        "endpoint": log_data.endpoint,
        "timestamp": datetime.now().isoformat(),
        "model_processing_time": round(processing_time, 4),
        "request_processing_time": round(total_time, 4),
    }

    logger.info(f"Logging entry: {log_entry}")

    log_key = f"log:{log_data.api_key}:{int(time.time())}"
    try:
        json_data = json.dumps(log_entry)
        memcached_client.set(log_key, json_data, expire=3600)

        keys_list_key = f"keys:{log_data.api_key}"
        existing_keys = memcached_client.get(keys_list_key)
        if existing_keys:
            existing_keys = json.loads(existing_keys)
        else:
            existing_keys = []
        
        existing_keys.append(log_key)
        memcached_client.set(keys_list_key, json.dumps(existing_keys), expire=3600)

    except TypeError as e:
        logger.error(f"JSON Serialization Error: {e}")

@app.get("/logs/")
def get_logs(request: Request):
    api_key = request.headers.get("Authorization")
    logs = []
    keys_list_key = f"keys:{api_key}"
    
    stored_keys = memcached_client.get(keys_list_key)
    if stored_keys: 
        stored_keys = json.loads(stored_keys)
        log_data = memcached_client.get_many(stored_keys)
        for key, value in log_data.items():
            logs.append(json.loads(value))
    
    return logs
