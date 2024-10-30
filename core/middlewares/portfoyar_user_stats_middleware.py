from django.contrib.auth.middleware import AuthenticationMiddleware
from core.utils import RedisInterface
from core.configs import (
    ONLINE_USERS_REDIS_DB,
    USER_STATS_REDIS_DB,
    USER_AGENTS_REDIS_DB,
)

online_redis_conn = RedisInterface(db=ONLINE_USERS_REDIS_DB)
user_stats_redis_conn = RedisInterface(db=USER_STATS_REDIS_DB)
user_agents_redis_conn = RedisInterface(db=USER_AGENTS_REDIS_DB)

ONLINE_USER_EX_TIME = 60 * 10  # 10 Minutes


class PortfoyarUserStatsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.auth_middleware = AuthenticationMiddleware(get_response)

    def __call__(self, request):
        ip = request.META.get("REMOTE_ADDR", "NOIP")
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        self.auth_middleware(request)
        username = request.user.username

        online_redis_conn.client.set(ip, username, ex=ONLINE_USER_EX_TIME)
        user_stats_redis_conn.client.set(ip, username)
        user_agents_redis_conn.client.set(user_agent, username)

        response = self.get_response(request)

        return response
