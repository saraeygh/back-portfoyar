import time
import os
import platform


from django.core.management.base import BaseCommand
from core.utils import clear_redis_cache, replace_all_arabic_letters_in_db
from core.configs import MANUAL_MODE

from core.tasks import is_market_open_today
from account.tasks import disable_expired_subscription
from account.utils import create_sub_for_all_no_sub_users, add_days_to_subs

from domestic_market.utils import get_dollar_price_history
from domestic_market.tasks import (
    calculate_commodity_mean_domestic,
    get_dollar_daily_price,
    populate_domestic_market_db,
    calculate_monthly_sell_domestic,
    calculate_production_sell_domestic,
    calculate_producers_yearly_value,
)

from fund.tasks import update_fund_info, get_all_fund_detail

from future_market.tasks import (
    update_derivative_info,
    update_future_base_equity,
    update_option_base_equity,
    update_future,
    update_option_result,
    check_future_active_contracts,
    check_option_active_contracts,
)
from global_market.tasks import calculate_commodity_means_global

from option_market.tasks import (
    update_option_data_from_tse,
    get_option_history,
    calculate_daily_option_value,
)

from stock_market.tasks import (
    update_market_watch,
    get_monthly_activity_report_letter,
    update_market_watch_indices,
    update_stock_full_raw_history,
    update_instrument_info,
    update_instrument_roi,
    stock_value_history,
    stock_option_value_history,
    stock_option_value_change,
    stock_option_price_spread,
    update_stock_daily_history,
    monitor_big_money,
)
from stock_market.utils import update_stock_adjusted_history


from dashboard.tasks import (
    dashboard_buy_sell_orders_value,
    dashboard_last_close_price,
    dashboard_total_index,
    dashboard_unweighted_index,
    dashboard_option_value_analysis,
    dashboard_change_percent_ranges_count,
    dashboard_market_money_flow,
)


def get_clear_cmd():
    if platform.system() == "Linux":
        clear_cmd = "clear"
    else:
        clear_cmd = "cls"

    return clear_cmd


def main_cli(clear_cmd):
    print(
        "Choose app:",
        "1) Account app",
        "2) Dashboard app",
        "3) Domestic market",
        "4) Fund app",
        "5) Future market",
        "6) Global market",
        "7) Option market",
        "8) Stock market",
        "10) Others",
        "0) Exit",
        sep="\n",
    )
    cmd = input("Enter command: ")
    os.system(clear_cmd)

    return cmd


def domestic_cli(clear_cmd):
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

            case _:
                print("Wrong choice!")
                time.sleep(0.5)
                continue


def global_cli(clear_cmd):
    while True:
        print(
            "Global market commands:",
            "all) Run all commands",
            "1) Calculate means",
            "0) Back",
            sep="\n",
        )
        cmd = input("Enter command: ")
        os.system(clear_cmd)
        match cmd:
            case "all":
                calculate_commodity_means_global()
            case "1":
                calculate_commodity_means_global()
            case "0":
                break

            case _:
                print("Wrong choice!")
                time.sleep(0.5)
                continue


def option_cli(clear_cmd):
    while True:
        print(
            "Option market commands:",
            "all) Run all commands",
            "1) Update option data",
            "2) Get option history",
            "3) calculate_daily_option_value",
            "0) Back",
            sep="\n",
        )
        cmd = input("Enter command: ")
        os.system(clear_cmd)
        match cmd:
            case "all":
                update_option_data_from_tse(MANUAL_MODE)
                get_option_history()
            case "1":
                update_option_data_from_tse(MANUAL_MODE)
            case "2":
                get_option_history()
            case "3":
                calculate_daily_option_value()
            case "0":
                break

            case _:
                print("Wrong choice!")
                time.sleep(0.5)
                continue


def stock_cli(clear_cmd):
    while True:
        print(
            "Stock market commands:",
            "all) Run all commands",
            "10) Update market watch & indices",
            "11) Update stock daily history",
            "12) Update instrument info",
            "13) Update instrument ROI",
            "14) Stock option price spread",
            "15) Stock value history & change",
            "16) Stock option value history",
            "17) Stock option value change",
            "18) update_stock_full_raw_history",
            "19) Update stock adjusted history",
            "20) Get monthly activity",
            "21) monitor_individual_influx",
            ##############################
            "0) Back",
            sep="\n",
        )
        cmd = input("Enter command: ")
        os.system(clear_cmd)
        match cmd:
            case "all":
                update_market_watch(MANUAL_MODE)
                update_market_watch_indices(MANUAL_MODE)
                update_instrument_info()
                update_instrument_roi(MANUAL_MODE)
                update_stock_daily_history()
                update_stock_full_raw_history()
                stock_value_history()
                stock_option_value_change(MANUAL_MODE)
                stock_option_price_spread(MANUAL_MODE)
                monitor_big_money(MANUAL_MODE)
                get_monthly_activity_report_letter()
            case "10":
                update_market_watch(MANUAL_MODE)
                update_market_watch_indices(MANUAL_MODE)
            case "11":
                update_stock_daily_history()
            case "12":
                update_instrument_info()
            case "13":
                update_instrument_roi(MANUAL_MODE)
            case "14":
                stock_option_price_spread(MANUAL_MODE)
            case "15":
                stock_value_history()
            case "16":
                stock_option_value_history()
            case "17":
                stock_option_value_change(MANUAL_MODE)
            case "18":
                update_stock_full_raw_history()
            case "19":
                update_stock_adjusted_history()
            case "20":
                get_monthly_activity_report_letter()
            case "21":
                monitor_big_money(MANUAL_MODE)
            case "0":
                break

            case _:
                print("Wrong choice!")
                time.sleep(0.5)
                continue


def future_cli(clear_cmd):
    while True:
        print(
            "Future market commands:",
            "all) Run all commands",
            "1) Update derivative info",
            "2) Update base equity",
            "3) Update future result",
            "4) Update option result",
            "5) Check active contracts",
            "0) Back",
            sep="\n",
        )
        cmd = input("Enter command: ")
        os.system(clear_cmd)
        match cmd:
            case "all":
                update_future_base_equity()
                update_option_base_equity()
                update_future()
                update_option_result()
                check_future_active_contracts()
                check_option_active_contracts()
            case "1":
                update_derivative_info()
            case "2":
                update_future_base_equity()
                update_option_base_equity()
            case "3":
                update_future()
            case "4":
                update_option_result()
            case "5":
                check_future_active_contracts()
                check_option_active_contracts()
            case "0":
                break

            case _:
                print("Wrong choice!")
                time.sleep(0.5)
                continue


def dashboard_cli(clear_cmd):
    while True:
        print(
            "Dashboard APP commands:",
            "all) Run all dashboard tasks",
            "Following tasks will be run:",
            "- dashboard_total_index",
            "- dashboard_unweighted_index",
            "- dashboard_buy_sell_orders_value",
            "- dashboard_last_close_price",
            "- dashboard_option_value_analysis",
            "- dashboard_change_percent_ranges_count",
            "- dashboard_market_money_flow",
            "0) Back",
            sep="\n",
        )
        cmd = input("Enter command: ")
        os.system(clear_cmd)
        match cmd:
            case "all":
                dashboard_buy_sell_orders_value(MANUAL_MODE)
                dashboard_last_close_price(MANUAL_MODE)
                dashboard_total_index(MANUAL_MODE)
                dashboard_unweighted_index(MANUAL_MODE)
                dashboard_option_value_analysis(MANUAL_MODE)
                dashboard_change_percent_ranges_count(MANUAL_MODE)
                dashboard_market_money_flow(MANUAL_MODE)
            case "0":
                break

            case _:
                print("Wrong choice!")
                time.sleep(0.5)
                continue


def fund_cli(clear_cmd):
    while True:
        print(
            "Fund APP commands:",
            "all) Run all commands",
            "1) Get all fund detail",
            "2) Update fund info",
            "0) Back",
            sep="\n",
        )
        cmd = input("Enter command: ")
        os.system(clear_cmd)
        match cmd:
            case "all":
                get_all_fund_detail()
                update_fund_info()
            case "1":
                get_all_fund_detail()
            case "2":
                update_fund_info()
            case "0":
                break

            case _:
                print("Wrong choice!")
                time.sleep(0.5)
                continue


def account_cli(clear_cmd):
    while True:
        print(
            "Account commands:",
            "1) Disable expired subscriptions",
            "2) create_sub_for_all_no_sub_users",
            "3) add_days_to_subs",
            "0) Back",
            sep="\n",
        )
        cmd = input("Enter command: ")
        os.system(clear_cmd)
        match cmd:
            case "1":
                disable_expired_subscription()
            case "2":
                create_sub_for_all_no_sub_users()
            case "3":
                add_days_to_subs()
            case "0":
                break

            case _:
                print("Wrong choice!")
                time.sleep(0.5)
                continue


def other_cli(clear_cmd):
    while True:
        print(
            "Other commands:",
            "all) Run all commands",
            "1) Clear redis cache",
            "2) Relpace all arabic letters",
            "3) is_market_open_today",
            "0) Back",
            sep="\n",
        )
        cmd = input("Enter command: ")
        os.system(clear_cmd)
        match cmd:
            case "all":
                clear_redis_cache()
                replace_all_arabic_letters_in_db()
            case "1":
                clear_redis_cache()
            case "2":
                replace_all_arabic_letters_in_db()
            case "3":
                is_market_open_today()
            case "0":
                break

            case _:
                print("Wrong choice!")
                time.sleep(0.5)
                continue


def night_tasks_cli():
    print("Running night tasks.")

    # ACCOUNT APP
    disable_expired_subscription()
    # DOMESTIC APP
    populate_domestic_market_db()
    calculate_commodity_mean_domestic()
    calculate_monthly_sell_domestic()
    calculate_production_sell_domestic()
    calculate_producers_yearly_value()
    # FUND APP
    update_fund_info()
    # FUTURE APP
    update_future_base_equity()
    update_option_base_equity()
    check_future_active_contracts()
    check_option_active_contracts()
    # OPTION APP
    get_option_history()
    # STOCK APP
    update_stock_daily_history()
    update_instrument_info()
    stock_value_history()
    stock_option_value_history()
    get_monthly_activity_report_letter()
    calculate_commodity_means_global()

    print("Night tasks done!")


class Command(BaseCommand):
    """Custom commands for tasks"""

    help = "Portfoyar CLI"

    def handle(self, *args, **options):
        clear_cmd = get_clear_cmd()

        while True:  # MAIN MENU
            cmd = main_cli(clear_cmd)

            match cmd:
                case "1":
                    account_cli(clear_cmd)

                case "2":
                    dashboard_cli(clear_cmd)

                case "3":
                    domestic_cli(clear_cmd)

                case "4":
                    fund_cli(clear_cmd)

                case "5":
                    future_cli(clear_cmd)

                case "6":
                    global_cli(clear_cmd)

                case "7":
                    option_cli(clear_cmd)

                case "8":
                    stock_cli(clear_cmd)

                case "10":
                    other_cli(clear_cmd)

                case "0":  # EXIT
                    break

                case "night-tasks":
                    night_tasks_cli()

                case _:
                    print("Wrong choice!")
                    time.sleep(0.5)
                    continue
