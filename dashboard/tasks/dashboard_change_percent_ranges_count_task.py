from core.configs import AUTO_MODE, MANUAL_MODE
from core.utils import run_main_task

from dashboard.utils import change_percent_ranges_count

from stock_market.utils import is_in_schedule


def dashboard_change_percent_ranges_count_main(run_mode: str):
    if run_mode == MANUAL_MODE or is_in_schedule(9, 0, 0, 12, 40, 0):
        change_percent_ranges_count()


def dashboard_change_percent_ranges_count(run_mode: str = AUTO_MODE):

    run_main_task(
        main_task=dashboard_change_percent_ranges_count_main,
        kw_args={"run_mode": run_mode},
    )
