import json
from datetime import datetime
from database import memcached_client

def log_request(api_key: str, endpoint: str):
    """Log user request to Memcached."""
    log_key = f"log:{api_key}"
    current_logs = memcached_client.get(log_key)

    if current_logs:
        logs = json.loads(current_logs)
    else:
        logs = []

    logs.append({"timestamp": datetime.utcnow().isoformat(), "endpoint": endpoint})
    
    # Store back in Memcached
    memcached_client.set(log_key, json.dumps(logs), time=3600)  # Store logs for 1 hour
