from dotenv import load_dotenv
import os
import redis

# Load environment variables
load_dotenv()

# Redis Setup for ml model cache
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=1)