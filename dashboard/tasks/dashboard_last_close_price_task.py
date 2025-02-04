from core.configs import AUTO_MODE, MANUAL_MODE
from core.utils import run_main_task

from dashboard.utils import last_close_price

from stock_market.utils import is_market_open


def dashboard_last_close_price_main(run_mode: str):
    if run_mode == MANUAL_MODE or is_market_open():
        last_close_price()


def dashboard_last_close_price(run_mode: str = AUTO_MODE):

    run_main_task(
        main_task=dashboard_last_close_price_main,
        kw_args={"run_mode": run_mode},
    )
