import jdatetime
from colorama import Fore, Style

from core.configs import TEHRAN_TZ

BLUE = "BLUE"
GREEN = "GREEN"
RED = "RED"


def print_task_info(color: str = BLUE, name: str = ""):
    now = f"⏰ [{jdatetime.datetime.now(tz=TEHRAN_TZ).strftime("%Y/%m/%d %H:%M:%S")}]"
    if color == GREEN:
        print(Fore.GREEN + now + " - " + name + " - Done" + Style.RESET_ALL)
    elif color == RED:
        print(Fore.RED + now + " - " + name + " - ERROR" + Style.RESET_ALL)
    else:
        print(Fore.BLUE + now + " - " + name + " - Running" + Style.RESET_ALL)

    return
