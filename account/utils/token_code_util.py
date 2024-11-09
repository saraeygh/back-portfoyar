import json
import random
from uuid import uuid4


from rest_framework import status
from rest_framework.response import Response

from core.utils import RedisInterface
from core.configs import KEY_WITH_EX_REDIS_DB, CODE_RANGE_MIN, CODE_RANGE_MAX


redis_conn = RedisInterface(db=KEY_WITH_EX_REDIS_DB)


def check_token_match(generated_token, sent_token):
    if sent_token != generated_token:
        return False, Response(
            {"message": "درخواست نامعتبر"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return True, "OK"


def check_code_match(generated_code, sent_code):
    if sent_code != generated_code:
        return False, Response(
            {"message": "کد ارسالی اشتباه است"}, status=status.HTTP_400_BAD_REQUEST
        )

    return True, "OK"


def set_dict_in_redis(code_info: dict, prefix: str, expiry: int):
    username = code_info.get("username")
    code_key = prefix + f"{username}"
    old_code_info = redis_conn.client.get(code_key)
    if old_code_info is not None:
        return False

    code_info = json.dumps(code_info)
    redis_conn.client.set(code_key, code_info, ex=expiry)
    return True


def code_token_generated_saved(username, prefix, expiry):
    code = str(random.randint(CODE_RANGE_MIN, CODE_RANGE_MAX))
    token = uuid4().hex
    code_saved_in_redis = set_dict_in_redis(
        {"username": username, "code": code, "token": token}, prefix, expiry
    )

    if not code_saved_in_redis:
        return (
            False,
            "",
            "",
            Response(
                {"message": "بعد از گذشت ۵ دقیقه دوباره تلاش کنید"},
                status=status.HTTP_400_BAD_REQUEST,
            ),
        )

    return True, code, token, ""
