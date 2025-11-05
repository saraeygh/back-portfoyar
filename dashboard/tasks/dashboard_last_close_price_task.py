from celery_singleton import Singleton
from samaneh.celery import app

from core.configs import AUTO_MODE, MANUAL_MODE
from core.utils import run_main_task, is_market_open_today

from dashboard.utils import last_close_price

from stock_market.utils import is_in_schedule


def dashboard_last_close_price_main(run_mode: str):
    if (
        is_in_schedule(9, 2, 0, 12, 32, 0) and is_market_open_today()
    ) or run_mode == MANUAL_MODE:
        last_close_price()


@app.task(base=Singleton, name="dashboard_last_close_price_task", expires=60)
def dashboard_last_close_price(run_mode: str = AUTO_MODE):

    run_main_task(
        main_task=dashboard_last_close_price_main,
        kw_args={"run_mode": run_mode},
    )
