from samaneh.settings.common import DEBUG

from rest_framework import status
from rest_framework.response import Response


from core.utils import (
    RedisInterface,
    DAILY_SIGNUP_TRY_LIMITATION,
)
from core.configs import KEY_WITH_EX_REDIS_DB, SIGNUP_TRY_COUNT_EXPIRY
from core.models import ACTIVE, FeatureToggle


redis_conn = RedisInterface(db=KEY_WITH_EX_REDIS_DB)


def check_daily_limitation(request):
    check_try_limitation = FeatureToggle.objects.filter(
        name=DAILY_SIGNUP_TRY_LIMITATION["name"]
    ).first()

    if check_try_limitation.state == ACTIVE:
        ip = request.META.get("REMOTE_ADDR", "")
        tried_count = redis_conn.client.get(ip)
        if tried_count is None:
            redis_conn.client.set(ip, 1, ex=SIGNUP_TRY_COUNT_EXPIRY)
            return False, ""

        else:
            today_tried_count = int(tried_count.decode("utf-8"))
            today_tried_count += 1
            if today_tried_count > int(check_try_limitation.value) and not DEBUG:
                limit_hours = int(SIGNUP_TRY_COUNT_EXPIRY / 3600)
                return True, Response(
                    {
                        "message": f"تعداد تلاش‌های شما بیشتر از حد مجاز ({int(check_try_limitation.value)}) شده است، لطفاً بعد از گذشت {limit_hours} ساعت دوباره تلاش کنید"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                time_left = redis_conn.client.ttl(ip)
                redis_conn.client.set(ip, today_tried_count, ex=time_left)

                return False, ""

    else:
        return False, ""
