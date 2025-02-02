from datetime import datetime
from app.database import memcached_client
import logging
import json
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def log_request(
        api_key: str, 
        endpoint: str,
        request_start_time: float,
        request_end_time: float,
        model_response_time: float
):
    """Log user request to Memcached."""
    processing_time = model_response_time - request_start_time
    total_time = request_end_time -request_start_time
    log_entry = {
        "api_key": api_key,
        "endpoint": endpoint,
        "timestamp": datetime.now().isoformat(),
        "request_start_time": datetime.fromtimestamp(request_start_time).isoformat(),
        "request_end_time": datetime.fromtimestamp(request_end_time).isoformat(),
        "model_processing_time": round(processing_time, 4),
        "request_processing_time": round(total_time, 4),
    }

    logger.info(f"logsss entry: {log_entry}")

    log_key = f"log:{api_key}:{int(time.time())}"
    try:
        json_data = json.dumps(log_entry)
        memcached_client.set(log_key, json_data, expire=3600)

        keys_list_key = f"keys:{api_key}"
        existing_keys = memcached_client.get(keys_list_key)
        if existing_keys:
            existing_keys = json.loads(existing_keys)
        else:
            existing_keys = []
        
        existing_keys.append(log_key)
        memcached_client.set(keys_list_key, json.dumps(existing_keys), expire=3600)

    except TypeError as e:
        logger.error(f"JSON Serialization Error: {e}")

def get_memechached_logs(api_key: str) -> list: 
    logs = []
    keys_list_key = f"keys:{api_key}"
    
    # Retrieve stored log keys
    stored_keys = memcached_client.get(keys_list_key)
    logger.info(f"stores keys: {stored_keys}")

    if stored_keys:
        stored_keys = json.loads(stored_keys)
        log_data = memcached_client.get_many(stored_keys)
        for key, value in log_data.items():
            logs.append(json.loads(value))
    
    return logs