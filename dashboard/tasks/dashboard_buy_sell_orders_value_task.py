from core.configs import AUTO_MODE, MANUAL_MODE
from core.utils import run_main_task

from dashboard.utils import buy_sell_orders_value

from stock_market.utils import is_in_schedule


def dashboard_buy_sell_orders_value_main(run_mode: str):
    if run_mode == MANUAL_MODE or is_in_schedule(9, 0, 0, 12, 40, 0):
        buy_sell_orders_value()


def dashboard_buy_sell_orders_value(run_mode: str = AUTO_MODE):

    run_main_task(
        main_task=dashboard_buy_sell_orders_value_main,
        kw_args={"run_mode": run_mode},
    )
