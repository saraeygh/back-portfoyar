from celery import shared_task

from core.configs import AUTO_MODE, MANUAL_MODE
from core.utils import run_main_task, is_market_open_today

from dashboard.utils import option_value_analysis, update_top_options

from stock_market.utils import is_in_schedule


def dashboard_option_value_analysis_main(run_mode: str):
    if (
        is_in_schedule(9, 2, 0, 12, 40, 0) and is_market_open_today()
    ) or run_mode == MANUAL_MODE:
        option_value_analysis()
        update_top_options()


@shared_task(name="dashboard_option_value_analysis_task", expires=60)
def dashboard_option_value_analysis(run_mode: str = AUTO_MODE):

    run_main_task(
        main_task=dashboard_option_value_analysis_main,
        kw_args={"run_mode": run_mode},
    )
