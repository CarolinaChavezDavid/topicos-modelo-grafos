from dotenv import load_dotenv
import os
import pymongo
import redis

# Load environment variables
load_dotenv()

# MongoDB Setup for users
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client["auth_db"]
users_collection = db["users"]

# Redis Setup for limiter
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)