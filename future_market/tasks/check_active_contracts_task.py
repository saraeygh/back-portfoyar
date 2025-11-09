from celery import shared_task

import pandas as pd

from core.utils import get_http_response, run_main_task

from future_market.models import FutureBaseEquity, OptionBaseEquity

ACTIVE_STATUS = "active_status"
SYMBOL = "symbol"
NAME = "name"
RENAME_COLS = {
    "وضعیت": ACTIVE_STATUS,
    "نماد معاملاتی": SYMBOL,
    "دارایی پایه": NAME,
}

IS_ACTIVE = "فعال"


def check_future_active_contracts_main():

    ACTIVE_CONTRACTS_URL = "https://www.ime.co.ir/list-gharardad-hayeati.html"
    response = get_http_response(req_url=ACTIVE_CONTRACTS_URL)
    contracts_table = (pd.read_html(response.text))[0]
    contracts_table.rename(columns=RENAME_COLS, inplace=True)

    active_contracts = set(
        contracts_table[contracts_table[ACTIVE_STATUS] == IS_ACTIVE][SYMBOL].to_list()
    )
    not_active_contracts = set(
        contracts_table[contracts_table[ACTIVE_STATUS] != IS_ACTIVE][SYMBOL].to_list()
    )

    active_base_equities = set(
        FutureBaseEquity.objects.all().values_list("derivative_symbol", flat=True)
    )

    not_added_contracts = active_contracts - active_base_equities
    if not_added_contracts:
        raise ValueError(f"not_added_contracts = {not_added_contracts}")

    deactivated_contracts = not_active_contracts & active_base_equities
    if deactivated_contracts:
        raise ValueError(f"deactivated_contracts = {deactivated_contracts}")


@shared_task(name="check_future_active_contracts_task")
def check_future_active_contracts():

    run_main_task(
        main_task=check_future_active_contracts_main,
        daily=True,
    )


def check_option_active_contracts_main():

    ACTIVE_CONTRACTS_URL = "https://www.ime.co.ir/ekhtiarm.html"
    response = get_http_response(req_url=ACTIVE_CONTRACTS_URL)
    contracts_table = (pd.read_html(response.text))[0]
    contracts_table.rename(columns=RENAME_COLS, inplace=True)

    active_contracts = set(
        contracts_table[contracts_table[ACTIVE_STATUS] == IS_ACTIVE][SYMBOL].to_list()
    )
    not_active_contracts = set(
        contracts_table[contracts_table[ACTIVE_STATUS] != IS_ACTIVE][SYMBOL].to_list()
    )

    active_base_equities = set(
        OptionBaseEquity.objects.all().values_list("derivative_symbol", flat=True)
    )

    new_added_contracts = active_contracts - active_base_equities
    if new_added_contracts:
        raise ValueError(f"not_added_contracts = {new_added_contracts}")

    deactivated_contracts = not_active_contracts & active_base_equities
    if deactivated_contracts:
        raise ValueError(f"deactivated_contracts = {deactivated_contracts}")


@shared_task(name="check_option_active_contracts_task")
def check_option_active_contracts():

    run_main_task(
        main_task=check_option_active_contracts_main,
        daily=True,
    )
