from core.utils import task_timing
from core.configs import AUTO_MODE, MANUAL_MODE

from stock_market.utils import is_market_open
from dashboard.utils import buy_sell_orders_value

from colorama import Fore, Style


@task_timing
def dashboard(run_mode: str = AUTO_MODE):

    if run_mode == MANUAL_MODE or is_market_open():

        print(Fore.BLUE + "updating buy_sell_orders_value ..." + Style.RESET_ALL)
        buy_sell_orders_value()
        print(Fore.GREEN + "updated buy_sell_orders_value" + Style.RESET_ALL)

    else:
        print(
            Fore.RED
            + __name__
            + " - "
            + "Not MANUAL_MODE or market is closed"
            + Style.RESET_ALL
        )
