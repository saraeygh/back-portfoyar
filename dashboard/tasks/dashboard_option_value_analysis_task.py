from core.configs import AUTO_MODE, MANUAL_MODE
from core.utils import run_main_task

from dashboard.utils import option_value_analysis, update_top_options

from stock_market.utils import is_in_schedule


def dashboard_option_value_analysis_main(run_mode: str):
    if run_mode == MANUAL_MODE or is_in_schedule(8, 40, 0, 12, 40, 0):
        option_value_analysis()
        update_top_options()


def dashboard_option_value_analysis(run_mode: str = AUTO_MODE):

    run_main_task(
        main_task=dashboard_option_value_analysis_main,
        kw_args={"run_mode": run_mode},
    )
