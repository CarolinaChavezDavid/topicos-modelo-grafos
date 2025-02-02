from fastapi_limiter.depends import RateLimiter
import aioredis
import os

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

def get_redis():
    return aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", encoding="utf-8", decode_responses=True)

def get_limiter(acount_type: str) -> RateLimiter:
    if acount_type == "FREEMIUM":
       return RateLimiter(times=3, seconds=60)
    else:
        return RateLimiter(times=5, seconds=60)
