import os
import pymongo
import pymemcache
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Setup for users
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client["auth_db"]
users_collection = db["users"]

# Memcached Setup (for request logs)
MEMCACHED_HOST = os.getenv("MEMCACHED_HOST", "memcached")
memcached_client = pymemcache.Client((MEMCACHED_HOST, 11211))
