import redis
from samaneh.settings.common import REDIS_HOST


def clear_redis_cache():
    host: str = REDIS_HOST
    port: int = 6379
    db: int = 2
    redis_client = redis.Redis(host=host, port=port, db=db)

    redis_client.flushdb()
