from celery import shared_task
from core.utils import task_timing, buy_sell_orders_value, is_scheduled
from core.configs import AUTO_MODE, MANUAL_MODE


@task_timing
@shared_task(name="dashboard_task")
def dashboard(run_mode: str = AUTO_MODE):
    if run_mode == MANUAL_MODE or is_scheduled(
        weekdays=[0, 1, 2, 3, 4], start_hour=8, start_min=45, end_hour=17
    ):
        buy_sell_orders_value()
