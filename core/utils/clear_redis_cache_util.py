import os
import redis


def clear_redis_cache():
    host: str = os.environ.setdefault("REDIS_SERVICE_NAME", "localhost")
    port: int = 6379
    db: int = 2
    redis_client = redis.Redis(host=host, port=port, db=db)

    redis_client.flushdb()
