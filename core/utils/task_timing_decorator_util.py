import time
from core.configs import TEHRAN_TZ
import jdatetime
from colorama import Style


def task_timing(received_task):
    def wrapper(*args, **kwargs):
        start = time.time()
        received_task()
        end = time.time()
        print(
            Style.BRIGHT
            + (
                f"⏰ [{jdatetime.datetime.now(tz=TEHRAN_TZ).strftime("%Y/%m/%d %H:%M:%S")}]"
                f" - {round(end - start)} Sec. {received_task.__name__}"
            )
            + Style.RESET_ALL
        )
        time.sleep(1)

    return wrapper
