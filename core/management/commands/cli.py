import time
import os
import platform
from colorama import Fore, Style

from django.core.management.base import BaseCommand
from core.utils import clear_redis_cache, replace_all_arabic_letters_in_db
from core.configs import MANUAL_MODE

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

from option_market.tasks import update_option_data_from_tse, get_option_history

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
)
from stock_market.utils import update_stock_adjusted_history


from dashboard.tasks import (
    dashboard_buy_sell_orders_value,
    dashboard_last_close_price,
    dashboard_total_index,
    dashboard_unweighted_index,
    dashboard_option_value_analysis,
)


def get_clear_cmd():
    if platform.system() == "Linux":
        clear_cmd = "clear"
    else:
        clear_cmd = "cls"

    return clear_cmd


def main_cli(clear_cmd):
    print(
        Style.BRIGHT + "Choose app:",
        Fore.BLUE + "1) Domestic market",
        "2) Global market",
        "3) Option market",
        "4) Stock market",
        "5) Future market",
        "6) Dashboard app",
        "7) Fund app",
        "9) Account app",
        Fore.RED + "10) Others",
        Fore.RED + "0) Exit" + Style.RESET_ALL,
        sep="\n",
    )
    cmd = input(Style.BRIGHT + "Enter command: " + Style.RESET_ALL)
    os.system(clear_cmd)

    return cmd


def domestic_cli(clear_cmd):
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

            case _:
                print(Style.BRIGHT + Fore.RED + "Wrong choice!" + Style.RESET_ALL)
                time.sleep(0.5)
                continue


def global_cli(clear_cmd):
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

            case _:
                print(Style.BRIGHT + Fore.RED + "Wrong choice!" + Style.RESET_ALL)
                time.sleep(0.5)
                continue


def option_cli(clear_cmd):
    while True:
        print(
            Style.BRIGHT + "Option market commands:",
            "all) Run all commands" + Style.RESET_ALL,
            Fore.BLUE + "1) Update option data",
            "2) Get option history",
            Fore.RED + "0) Back" + Style.RESET_ALL,
            sep="\n",
        )
        cmd = input(Style.BRIGHT + "Enter command: " + Style.RESET_ALL)
        os.system(clear_cmd)
        match cmd:
            case "all":
                update_option_data_from_tse(MANUAL_MODE)
                get_option_history()
            case "1":
                update_option_data_from_tse(MANUAL_MODE)
            case "2":
                get_option_history()
            case "0":
                break

            case _:
                print(Style.BRIGHT + Fore.RED + "Wrong choice!" + Style.RESET_ALL)
                time.sleep(0.5)
                continue


def stock_cli(clear_cmd):
    while True:
        print(
            Style.BRIGHT + "Stock market commands:",
            "all) Run all commands" + Style.RESET_ALL,
            Fore.BLUE + "1) Get monthly activity",
            "2) Update market watch",
            "3) Update instrument history",
            "4) Update instrument info",
            "5) Update instrument ROI",
            "6) Stock value change",
            "7) Stock option value history",
            "8) Stock option value change",
            "9) Stock option price spread",
            "10) Update stock adjusted history",
            "11) Update stock daily history",
            Fore.RED + "0) Back" + Style.RESET_ALL,
            sep="\n",
        )
        cmd = input(Style.BRIGHT + "Enter command: " + Style.RESET_ALL)
        os.system(clear_cmd)
        match cmd:
            case "all":
                update_market_watch(MANUAL_MODE)
                update_market_watch_indices(MANUAL_MODE)
                update_instrument_info()
                update_instrument_roi(MANUAL_MODE)
                update_stock_daily_history(MANUAL_MODE)
                update_stock_full_raw_history()
                stock_value_history()
                stock_option_value_change(MANUAL_MODE)
                stock_option_price_spread(MANUAL_MODE)
                get_monthly_activity_report_letter()
            case "1":
                get_monthly_activity_report_letter()
            case "2":
                update_market_watch(MANUAL_MODE)
            case "3":
                update_stock_full_raw_history()
            case "4":
                update_instrument_info()
            case "5":
                update_instrument_roi(MANUAL_MODE)
            case "6":
                stock_value_history()
            case "7":
                stock_option_value_history()
            case "8":
                stock_option_value_change(MANUAL_MODE)
            case "9":
                stock_option_price_spread(MANUAL_MODE)
            case "10":
                update_stock_adjusted_history()
            case "11":
                update_stock_daily_history(MANUAL_MODE)
            case "0":
                break

            case _:
                print(Style.BRIGHT + Fore.RED + "Wrong choice!" + Style.RESET_ALL)
                time.sleep(0.5)
                continue


def future_cli(clear_cmd):
    while True:
        print(
            Style.BRIGHT + "Future market commands:",
            "all) Run all commands" + Style.RESET_ALL,
            Fore.BLUE + "1) Update derivative info",
            "2) Update base equity",
            "3) Update future result",
            "4) Update option result",
            "5) Check active contracts",
            Fore.RED + "0) Back" + Style.RESET_ALL,
            sep="\n",
        )
        cmd = input(Style.BRIGHT + "Enter command: " + Style.RESET_ALL)
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
                print(Style.BRIGHT + Fore.RED + "Wrong choice!" + Style.RESET_ALL)
                time.sleep(0.5)
                continue


def dashboard_cli(clear_cmd):
    while True:
        print(
            Style.BRIGHT + "Dashboard APP commands:",
            "all) Run all dashboard tasks",
            Fore.CYAN + "Following tasks will be run:" + Style.RESET_ALL,
            Fore.BLUE + "- dashboard_total_index",
            Fore.BLUE + "- dashboard_unweighted_index",
            Fore.BLUE + "- dashboard_buy_sell_orders_value",
            Fore.BLUE + "- dashboard_last_close_price",
            Fore.BLUE + "- dashboard_option_value_analysis",
            Fore.RED + "0) Back" + Style.RESET_ALL,
            sep="\n",
        )
        cmd = input(Style.BRIGHT + "Enter command: " + Style.RESET_ALL)
        os.system(clear_cmd)
        match cmd:
            case "all":
                dashboard_buy_sell_orders_value(MANUAL_MODE)
                dashboard_last_close_price(MANUAL_MODE)
                dashboard_total_index(MANUAL_MODE)
                dashboard_unweighted_index(MANUAL_MODE)
                dashboard_option_value_analysis(MANUAL_MODE)
            case "0":
                break

            case _:
                print(Style.BRIGHT + Fore.RED + "Wrong choice!" + Style.RESET_ALL)
                time.sleep(0.5)
                continue


def fund_cli(clear_cmd):
    while True:
        print(
            Style.BRIGHT + "Fund APP commands:",
            "all) Run all commands" + Style.RESET_ALL,
            Fore.BLUE + "1) Get all fund detail",
            "2) Update fund info",
            Fore.RED + "0) Back" + Style.RESET_ALL,
            sep="\n",
        )
        cmd = input(Style.BRIGHT + "Enter command: " + Style.RESET_ALL)
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
                print(Style.BRIGHT + Fore.RED + "Wrong choice!" + Style.RESET_ALL)
                time.sleep(0.5)
                continue


def account_cli(clear_cmd):
    while True:
        print(
            Style.BRIGHT + "Account commands:" + Style.RESET_ALL,
            Fore.BLUE + "1) Disable expired subscriptions",
            "2) create_sub_for_all_no_sub_users",
            "3) add_days_to_subs",
            Fore.RED + "0) Back" + Style.RESET_ALL,
            sep="\n",
        )
        cmd = input(Style.BRIGHT + "Enter command: " + Style.RESET_ALL)
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
                print(Style.BRIGHT + Fore.RED + "Wrong choice!" + Style.RESET_ALL)
                time.sleep(0.5)
                continue


def other_cli(clear_cmd):
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

            case _:
                print(Style.BRIGHT + Fore.RED + "Wrong choice!" + Style.RESET_ALL)
                time.sleep(0.5)
                continue


def night_tasks_cli():
    print(Fore.BLUE + "Running night tasks." + Style.RESET_ALL)

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

    print(Fore.GREEN + "Night tasks done!" + Style.RESET_ALL)


class Command(BaseCommand):
    """Custom commands for tasks"""

    help = "Portfoyar CLI"

    def handle(self, *args, **options):
        clear_cmd = get_clear_cmd()

        while True:  # MAIN MENU
            cmd = main_cli(clear_cmd)

            match cmd:
                case "1":
                    domestic_cli(clear_cmd)

                case "2":
                    global_cli(clear_cmd)

                case "3":
                    option_cli(clear_cmd)

                case "4":
                    stock_cli(clear_cmd)

                case "5":
                    future_cli(clear_cmd)

                case "6":
                    dashboard_cli(clear_cmd)

                case "7":
                    fund_cli(clear_cmd)

                case "9":
                    account_cli(clear_cmd)

                case "10":
                    other_cli(clear_cmd)

                case "0":  # EXIT
                    break

                case "night-tasks":
                    night_tasks_cli()

                case _:
                    print(Style.BRIGHT + Fore.RED + "Wrong choice!" + Style.RESET_ALL)
                    time.sleep(0.5)
                    continue
