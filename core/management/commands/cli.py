import time
import os
import platform


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

from future_market.tasks import update_future_info, update_base_equity
from global_market.tasks import calculate_commodity_means_global

from option_market.tasks import (
    update_option_data_from_tse,
    get_option_history,
    populate_option_total_volume,
    option_volume_strategy_result,
)
from option_market.utils import populate_all_option_strategy

from stock_market.tasks import (
    get_monthly_activity_report_letter,
    stock_market_watch,
    update_stock_raw_adjusted_history,
    update_instrument_info,
    update_instrument_roi,
    stock_value_history,
    stock_value_change,
    stock_option_value_change,
    stock_option_price_spread,
)
from stock_market.utils import update_stock_adjusted_history


class Command(BaseCommand):
    """Custom commands for tasks"""

    help = "Portfoyar CLI"

    def handle(self, *args, **options):
        # DEFINE OS CLEAR COMMAND LINE
        if platform.system() == "Linux":
            CLEAR_CMD = "clear"
        else:
            CLEAR_CMD = "cls"

        while True:  # MAIN MENU
            print(
                "Choose app:",
                "1) Domestic market",
                "2) Global market",
                "3) Option market",
                "4) Stock market",
                "5) Future market",
                "9) Others",
                "0) Exit",
                sep="\n",
            )
            cmd = input("Enter command: ")
            os.system(CLEAR_CMD)

            match cmd:
                case "1":  # DOMESTIC MARKET
                    while True:
                        print(
                            "Domestic market commands:",
                            "all) Run all commands",
                            "1) Get trades",
                            "2) Calculate means",
                            "3) Get dollar price",
                            "4) Calculate monthly sell",
                            "5) Calculate production sell",
                            "6) Get dollar price history",
                            "7) Calculate producers yearly value",
                            "0) Back",
                            sep="\n",
                        )
                        cmd = input("Enter command: ")
                        os.system(CLEAR_CMD)
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
                case "2":  # GLOBAL MARKET
                    while True:
                        print(
                            "Global market commands:",
                            "all) Run all commands",
                            "1) Calculate means",
                            "0) Back",
                            sep="\n",
                        )
                        cmd = input("Enter command: ")
                        os.system(CLEAR_CMD)
                        match cmd:
                            case "all":
                                calculate_commodity_means_global()
                            case "1":
                                calculate_commodity_means_global()
                            case "0":
                                break
                case "3":  # OPTION MARKET
                    while True:
                        print(
                            "Option market commands:",
                            "all) Run all commands",
                            "1) Update option data",
                            "2) Populate all option strategies",
                            "3) Get option history",
                            "4) Populate option total volume",
                            "5) Option volume strategy result",
                            "0) Back",
                            sep="\n",
                        )
                        cmd = input("Enter command: ")
                        os.system(CLEAR_CMD)
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
                case "4":  # STOCK MARKET
                    while True:
                        print(
                            "Stock market commands:",
                            "all) Run all commands",
                            "1) Get monthly activity",
                            "2) Update market watch",
                            "3) Update instrument history",
                            "4) Update instrument info",
                            "5) Update instrument ROI",
                            "6) Stock value history",
                            "7) Stock value change",
                            "8) Stock option value change",
                            "9) Stock option price spread",
                            "10) Update stock adjusted history",
                            "0) Back",
                            sep="\n",
                        )
                        cmd = input("Enter command: ")
                        os.system(CLEAR_CMD)
                        match cmd:
                            case "all":
                                stock_market_watch()
                                update_instrument_info()
                                update_instrument_roi()
                                update_stock_raw_adjusted_history()
                                stock_value_history()
                                stock_value_change()
                                stock_option_value_change()
                                stock_option_price_spread()
                                get_monthly_activity_report_letter()
                            case "1":
                                get_monthly_activity_report_letter()
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
                            case "7":
                                stock_value_change()
                            case "8":
                                stock_option_value_change()
                            case "9":
                                stock_option_price_spread()
                            case "10":
                                update_stock_adjusted_history()
                            case "0":
                                break

                case "5":  # FUTURE MARKET
                    while True:
                        print(
                            "Future market commands:",
                            "all) Run all commands",
                            "1) Update future info",
                            "2) Update base equity",
                            "0) Back",
                            sep="\n",
                        )
                        cmd = input("Enter command: ")
                        os.system(CLEAR_CMD)
                        match cmd:
                            case "all":
                                update_future_info()
                                update_base_equity()
                            case "1":
                                update_future_info()
                            case "2":
                                update_base_equity()
                            case "0":
                                break

                case "9":  # OTHERS
                    while True:
                        print(
                            "Other commands:",
                            "all) Run all commands",
                            "1) Clear redis cache",
                            "2) Relpace all arabic letters",
                            "0) Back",
                            sep="\n",
                        )
                        cmd = input("Enter command: ")
                        os.system(CLEAR_CMD)
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

                case "99":  # RUN ALL COMMANDS
                    clear_redis_cache()

                    update_future_info()

                    calculate_commodity_means_global()

                    get_dollar_daily_price()

                    populate_domestic_market_db()

                    calculate_producers_yearly_value()

                    calculate_commodity_mean_domestic()

                    calculate_monthly_sell_domestic()

                    calculate_production_sell_domestic()

                    stock_market_watch()

                    update_stock_raw_adjusted_history()

                    stock_value_history()

                    stock_value_change()

                    stock_option_value_change()

                    stock_option_price_spread()

                    update_instrument_info()

                    update_instrument_roi()

                    update_option_data_from_tse()

                    get_option_history()

                    populate_option_total_volume()

                    option_volume_strategy_result()

                    get_monthly_activity_report_letter()

                case _:
                    print("Wrong choice!!!")
                    time.sleep(0.5)
                    continue
