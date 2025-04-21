from core.configs import AUTO_MODE, MANUAL_MODE
from core.utils import run_main_task, is_market_open_today

from dashboard.utils import get_total_index_from_tse

from stock_market.utils import is_in_schedule


def dashboard_total_index_main(run_mode: str):
    if (
        is_in_schedule(9, 2, 0, 12, 40, 0) and is_market_open_today()
    ) or run_mode == MANUAL_MODE:
        get_total_index_from_tse()


def dashboard_total_index(run_mode: str = AUTO_MODE):

    run_main_task(
        main_task=dashboard_total_index_main,
        kw_args={"run_mode": run_mode},
    )
