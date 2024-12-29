from core.configs import AUTO_MODE, MANUAL_MODE
from core.utils import run_main_task, print_task_info

from stock_market.utils import is_market_open

from dashboard.utils import buy_sell_orders_value, last_close_price


def dashboard_main(run_mode: str):
    if run_mode == MANUAL_MODE or is_market_open():
        print_task_info(name=buy_sell_orders_value.__name__)
        buy_sell_orders_value()

        print_task_info(name=last_close_price.__name__)
        last_close_price()


def dashboard(run_mode: str = AUTO_MODE):

    run_main_task(
        main_task=dashboard_main,
        kw_args={"run_mode": run_mode},
    )
