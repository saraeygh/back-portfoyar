import time


def task_timing(received_task):
    def wrapper():
        start = time.time()
        received_task()
        end = time.time()
        print(
            f"⏰⏰⏰ Elapsed time: {round(end - start)} seconds. {received_task.__name__}"
        )
        print("")
        time.sleep(1)

    return wrapper
