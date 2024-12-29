from core.configs import AUTO_MODE, MANUAL_MODE
from core.utils import print_task_info, send_task_fail_success_email

from stock_market.utils import is_market_open
from dashboard.utils import buy_sell_orders_value, last_close_price


def dashboard_main(run_mode: str = AUTO_MODE):
    if run_mode == MANUAL_MODE or is_market_open():
        print_task_info(name=buy_sell_orders_value.__name__)
        buy_sell_orders_value()

        print_task_info(name=last_close_price.__name__)
        last_close_price()

    else:
        print_task_info(
            color="RED", name=dashboard_main.__name__ + "!MANUAL_MODE | Closed"
        )


def dashboard(run_mode: str = AUTO_MODE):
    TASK_NAME = dashboard.__name__
    print_task_info(name=TASK_NAME)

    try:
        dashboard_main(run_mode)
    except Exception as e:
        send_task_fail_success_email(task_name=TASK_NAME, exception=e)

    print_task_info(color="GREEN", name=TASK_NAME)
