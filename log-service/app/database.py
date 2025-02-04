import os
import pymemcache
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Memcached Setup (for request logs)
MEMCACHED_HOST = os.getenv("MEMCACHED_HOST", "memcached")
memcached_client = pymemcache.Client((MEMCACHED_HOST, 11211))
