from pytz import timezone

import jdatetime


def is_scheduled(weekdays: list, start: int, end: int):
    tehran = timezone("Asia/Tehran")
    now = jdatetime.datetime.now(tz=tehran)
    print("NOW: >>>>>>>>>>>>>>", now)
    weekday = now.weekday()
    hour = now.hour
    if weekday in weekdays and (start <= hour <= end):
        return True
    return False
