import json

from rest_framework import status
from rest_framework.response import Response

from core.utils import RedisInterface
from core.configs import KEY_WITH_EX_REDIS_DB


def get_dict_from_redis(username, prefix):
    redis_conn = RedisInterface(db=KEY_WITH_EX_REDIS_DB)
    code_key = prefix + f"{username}"
    code_info = redis_conn.client.get(code_key)

    return None if code_info is None else json.loads(code_info.decode("utf-8"))


def check_code_expiry(username, prefix):
    code_info = get_dict_from_redis(username, prefix)
    if code_info is None:
        return True, Response(
            {"message": "کد منقضی شده است، لطفا دوباره تلاش کنید"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return False, code_info
