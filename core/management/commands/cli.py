import time
import os
import platform
from colorama import Fore, Style

from django.core.management.base import BaseCommand
from core.utils import clear_redis_cache, replace_all_arabic_letters_in_db
from domestic_market.utils import get_dollar_price_history
from domestic_market.tasks import (
    calculate_commodity_mean_domestic,
    get_dollar_daily_price,
    populate_domestic_market_db,
    calculate_monthly_sell_domestic,
    calculate_production_sell_domestic,
    calculate_producers_yearly_value,
)

from future_market.tasks import (
    update_derivative_info,
    update_base_equity,
    update_future,
    update_option_result,
)
from global_market.tasks import calculate_commodity_means_global

from option_market.tasks import (
    update_option_data_from_tse,
    get_option_history,
    populate_option_total_volume,
    option_volume_strategy_result,
)
from option_market.utils import populate_all_option_strategy

from stock_market.tasks import (
    update_market_watch,
    get_monthly_activity_report_letter,
    stock_market_watch,
    update_stock_raw_adjusted_history,
    update_instrument_info,
    update_instrument_roi,
    stock_value_history,
    stock_option_value_change,
    stock_option_price_spread,
)
from stock_market.utils import update_stock_adjusted_history


def get_clear_cmd():
    if platform.system() == "Linux":
        clear_cmd = "clear"
    else:
        clear_cmd = "cls"

    return clear_cmd


class Command(BaseCommand):
    """Custom commands for tasks"""

    help = "Portfoyar CLI"

    def handle(self, *args, **options):
        clear_cmd = get_clear_cmd()

        #######################################################################
        while True:  # MAIN MENU
            print(
                Style.BRIGHT + "Choose app:",
                Fore.BLUE + "1) Domestic market",
                "2) Global market",
                "3) Option market",
                "4) Stock market",
                "5) Future market",
                Fore.RED + "9) Others",
                Fore.RED + "0) Exit" + Style.RESET_ALL,
                sep="\n",
            )
            cmd = input(Style.BRIGHT + "Enter command: " + Style.RESET_ALL)
            os.system(clear_cmd)

            match cmd:
                ###############################################################
                case "1":  # DOMESTIC MARKET
                    while True:
                        print(
                            Style.BRIGHT + "Domestic market commands:",
                            "all) Run all commands" + Style.RESET_ALL,
                            Fore.BLUE + "1) Get trades",
                            "2) Calculate means",
                            "3) Get dollar price",
                            "4) Calculate monthly sell",
                            "5) Calculate production sell",
                            "6) Get dollar price history",
                            "7) Calculate producers yearly value",
                            Fore.RED + "0) Back" + Style.RESET_ALL,
                            sep="\n",
                        )
                        cmd = input(Style.BRIGHT + "Enter command: " + Style.RESET_ALL)
                        os.system(clear_cmd)
                        match cmd:
                            case "all":
                                get_dollar_daily_price()
                                populate_domestic_market_db()
                                calculate_producers_yearly_value()
                                calculate_commodity_mean_domestic()
                                calculate_monthly_sell_domestic()
                                calculate_production_sell_domestic()
                            case "1":
                                populate_domestic_market_db()
                            case "2":
                                calculate_commodity_mean_domestic()
                            case "3":
                                get_dollar_daily_price()
                            case "4":
                                calculate_monthly_sell_domestic()
                            case "5":
                                calculate_production_sell_domestic()
                            case "6":
                                get_dollar_price_history()
                            case "7":
                                calculate_producers_yearly_value()
                            case "0":
                                break
                ###############################################################
                case "2":  # GLOBAL MARKET
                    while True:
                        print(
                            Style.BRIGHT + "Global market commands:",
                            "all) Run all commands" + Style.RESET_ALL,
                            Fore.BLUE + "1) Calculate means",
                            Fore.RED + "0) Back" + Style.RESET_ALL,
                            sep="\n",
                        )
                        cmd = input(Style.BRIGHT + "Enter command: " + Style.RESET_ALL)
                        os.system(clear_cmd)
                        match cmd:
                            case "all":
                                calculate_commodity_means_global()
                            case "1":
                                calculate_commodity_means_global()
                            case "0":
                                break
                ###############################################################
                case "3":  # OPTION MARKET
                    while True:
                        print(
                            Style.BRIGHT + "Option market commands:",
                            "all) Run all commands" + Style.RESET_ALL,
                            Fore.BLUE + "1) Update option data",
                            "2) Populate all option strategies",
                            "3) Get option history",
                            "4) Populate option total volume",
                            "5) Option volume strategy result",
                            Fore.RED + "0) Back" + Style.RESET_ALL,
                            sep="\n",
                        )
                        cmd = input(Style.BRIGHT + "Enter command: " + Style.RESET_ALL)
                        os.system(clear_cmd)
                        match cmd:
                            case "all":
                                update_option_data_from_tse()
                                populate_all_option_strategy()
                                get_option_history()
                                populate_option_total_volume()
                                option_volume_strategy_result()
                            case "1":
                                update_option_data_from_tse()
                            case "2":
                                populate_all_option_strategy()
                            case "3":
                                get_option_history()
                            case "4":
                                populate_option_total_volume()
                            case "5":
                                option_volume_strategy_result()
                            case "0":
                                break
                ###############################################################
                case "4":  # STOCK MARKET
                    while True:
                        print(
                            Style.BRIGHT + "Stock market commands:",
                            "all) Run all commands" + Style.RESET_ALL,
                            Fore.BLUE + "1) Get monthly activity",
                            "22) Update market watch (new)",
                            "2) Update market watch",
                            "3) Update instrument history",
                            "4) Update instrument info",
                            "5) Update instrument ROI",
                            "6) Stock value change",
                            "8) Stock option value change",
                            "9) Stock option price spread",
                            "10) Update stock adjusted history",
                            Fore.RED + "0) Back" + Style.RESET_ALL,
                            sep="\n",
                        )
                        cmd = input(Style.BRIGHT + "Enter command: " + Style.RESET_ALL)
                        os.system(clear_cmd)
                        match cmd:
                            case "all":
                                update_market_watch()
                                stock_market_watch()
                                update_instrument_info()
                                update_instrument_roi()
                                update_stock_raw_adjusted_history()
                                stock_value_history()
                                stock_option_value_change()
                                stock_option_price_spread()
                                get_monthly_activity_report_letter()
                            case "1":
                                get_monthly_activity_report_letter()
                            case "22":
                                update_market_watch()
                            case "2":
                                stock_market_watch()
                            case "3":
                                update_stock_raw_adjusted_history()
                            case "4":
                                update_instrument_info()
                            case "5":
                                update_instrument_roi()
                            case "6":
                                stock_value_history()
                            case "8":
                                stock_option_value_change()
                            case "9":
                                stock_option_price_spread()
                            case "10":
                                update_stock_adjusted_history()
                            case "0":
                                break
                ###############################################################
                case "5":  # FUTURE MARKET
                    while True:
                        print(
                            Style.BRIGHT + "Future market commands:",
                            "all) Run all commands" + Style.RESET_ALL,
                            Fore.BLUE + "1) Update derivative info",
                            "2) Update base equity",
                            "3) Update future result",
                            "4) Update option result",
                            Fore.RED + "0) Back" + Style.RESET_ALL,
                            sep="\n",
                        )
                        cmd = input(Style.BRIGHT + "Enter command: " + Style.RESET_ALL)
                        os.system(clear_cmd)
                        match cmd:
                            case "all":
                                update_base_equity()
                                update_future()
                                update_option_result()
                            case "1":
                                update_derivative_info()
                            case "2":
                                update_base_equity()
                            case "3":
                                update_future()
                            case "4":
                                update_option_result()
                            case "0":
                                break

                case "9":  # OTHERS
                    while True:
                        print(
                            Style.BRIGHT + "Other commands:",
                            "all) Run all commands" + Style.RESET_ALL,
                            Fore.BLUE + "1) Clear redis cache",
                            "2) Relpace all arabic letters",
                            Fore.RED + "0) Back" + Style.RESET_ALL,
                            sep="\n",
                        )
                        cmd = input(Style.BRIGHT + "Enter command: " + Style.RESET_ALL)
                        os.system(clear_cmd)
                        match cmd:
                            case "all":
                                clear_redis_cache()
                                replace_all_arabic_letters_in_db()
                            case "1":
                                clear_redis_cache()
                            case "2":
                                replace_all_arabic_letters_in_db()
                            case "0":
                                break
                case "0":  # EXIT
                    break

                case _:
                    print(Style.BRIGHT + Fore.RED + "Wrong choice!" + Style.RESET_ALL)
                    time.sleep(0.5)
                    continue
