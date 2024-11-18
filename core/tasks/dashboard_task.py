from celery import shared_task
from core.utils import task_timing, buy_sell_orders_value, is_scheduled
from core.configs import AUTO_MODE, MANUAL_MODE
from stock_market.utils import is_market_open
from colorama import Fore, Style


@task_timing
@shared_task(name="dashboard_task")
def dashboard(run_mode: str = AUTO_MODE):

    # if run_mode == MANUAL_MODE or (
    #     is_scheduled(weekdays=[0, 1, 2, 3, 4], start_hour=8, start_min=45, end_hour=17)
    #     and is_market_open()
    # ):

    if run_mode == MANUAL_MODE or is_market_open():
        print(Fore.BLUE + "updating buy_sell_orders_value ..." + Style.RESET_ALL)
        buy_sell_orders_value()
        print(Fore.GREEN + "updated buy_sell_orders_value" + Style.RESET_ALL)
