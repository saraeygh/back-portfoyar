from datetime import datetime
import pytz
from core.configs import TEHRAN_TZ


def get_relative_datetime(datetime_obj):

    datetime_obj = datetime_obj.replace(tzinfo=TEHRAN_TZ)
    now = datetime.now(tz=TEHRAN_TZ)

    diff = now - datetime_obj
    seconds = int(diff.total_seconds())
    minutes = int(seconds / 60)
    hours = int(seconds / 3600)  # (60 * 60)
    days = int(seconds / 86400)  # (60 * 60 * 24)
    months = int(seconds / 2592000)  # (60 * 60 * 24 * 30)
    years = int(seconds / 31104000)  # (60 * 60 * 24 * 30 * 12)

    if years > 0:
        return f"{years} سال پیش"
    elif months > 0:
        return f"{months} ماه پیش"
    elif days > 0:
        return f"{days} روز پیش"
    elif hours > 0:
        return f"{hours} ساعت پیش"
    elif minutes > 0:
        return f"{minutes} دقیقه پیش"
    else:
        return f"{seconds} ثانیه پیش"
