import pandas as pd

from core.utils import print_task_info, get_http_response, send_task_fail_success_email
from future_market.models import BaseEquity

ACTIVE_STATUS = "active_status"
SYMBOL = "symbol"
RENAME_COLS = {
    "وضعیت": ACTIVE_STATUS,
    "نماد معاملاتی": SYMBOL,
}

IS_ACTIVE = "فعال"
IS_NOT_ACTIVE = "غیرفعال"


def check_active_contracts_main():

    ACTIVE_CONTRACTS_URL = "https://www.ime.co.ir/list-gharardad-hayeati.html"
    response = get_http_response(req_url=ACTIVE_CONTRACTS_URL, req_headers={})
    contracts_table = (pd.read_html(response.text))[0]
    contracts_table.rename(columns=RENAME_COLS, inplace=True)

    active_contracts = set(
        contracts_table[contracts_table[ACTIVE_STATUS] == IS_ACTIVE][SYMBOL].to_list()
    )
    not_active_contracts = set(
        contracts_table[contracts_table[ACTIVE_STATUS] == IS_NOT_ACTIVE][
            SYMBOL
        ].to_list()
    )

    active_base_equities = set(
        BaseEquity.objects.all().values_list("derivative_symbol", flat=True)
    )

    not_added_contracts = active_contracts - active_base_equities
    if not_added_contracts:
        raise ValueError(f"not_added_contracts = {not_added_contracts}")

    deactivated_contracts = not_active_contracts & active_base_equities
    if deactivated_contracts:
        raise ValueError(f"deactivated_contracts = {deactivated_contracts}")


def check_active_contracts():
    TASK_NAME = check_active_contracts.__name__
    print_task_info(name=TASK_NAME)

    try:
        check_active_contracts_main()
        send_task_fail_success_email(task_name=TASK_NAME)
    except Exception as e:
        send_task_fail_success_email(task_name=TASK_NAME, exception=e)

    print_task_info(color="GREEN", name=TASK_NAME)
