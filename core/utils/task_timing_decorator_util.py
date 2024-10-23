import time
from colorama import Style


def task_timing(received_task):
    def wrapper():
        start = time.time()
        received_task()
        end = time.time()
        print(
            Style.BRIGHT
            + f"⏰⏰⏰ Elapsed time: {round(end - start)} seconds. {received_task.__name__}"
            + Style.RESET_ALL
        )
        time.sleep(1)

    return wrapper
