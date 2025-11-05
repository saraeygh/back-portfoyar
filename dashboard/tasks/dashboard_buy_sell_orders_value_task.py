from celery_singleton import Singleton
from samaneh.celery import app

from core.configs import AUTO_MODE, MANUAL_MODE
from core.utils import run_main_task, is_market_open_today

from dashboard.utils import buy_sell_orders_value

from stock_market.utils import is_in_schedule


def dashboard_buy_sell_orders_value_main(run_mode: str):
    if (
        is_in_schedule(9, 2, 0, 12, 32, 0) and is_market_open_today()
    ) or run_mode == MANUAL_MODE:
        buy_sell_orders_value()


@app.task(base=Singleton, name="dashboard_buy_sell_orders_value_task", expires=60)
def dashboard_buy_sell_orders_value(run_mode: str = AUTO_MODE):

    run_main_task(
        main_task=dashboard_buy_sell_orders_value_main,
        kw_args={"run_mode": run_mode},
    )
