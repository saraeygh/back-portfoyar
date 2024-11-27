from core.configs import AUTO_MODE, MANUAL_MODE
from core.utils import print_task_info

from stock_market.utils import is_market_open
from dashboard.utils import buy_sell_orders_value


def dashboard(run_mode: str = AUTO_MODE):
    print_task_info(name=__name__)

    if run_mode == MANUAL_MODE or is_market_open():

        print_task_info(name="buy_sell_orders_value")
        buy_sell_orders_value()

    else:
        print_task_info(color="RED", name=__name__ + "!MANUAL_MODE | Closed")

    print_task_info(color="GREEN", name=__name__)
