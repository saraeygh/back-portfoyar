from pytz import timezone

import jdatetime


def is_scheduled(
    weekdays: list,
    start_hour: int = 8,
    start_min: int = 0,
    end_hour: int = 17,
    end_min: int = 0,
):
    tehran = timezone("Asia/Tehran")
    now = jdatetime.datetime.now(tz=tehran)
    weekday = now.weekday()
    hour = now.hour
    minute = now.minute

    if weekday in weekdays and (
        (start_hour == hour and minute > start_min)
        or (start_hour < hour < end_hour)
        or (end_hour == hour and minute < end_min)
    ):
        return True

    return False
