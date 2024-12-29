import json
import pandas as pd

from colorama import Fore, Style

from core.utils import RedisInterface, print_task_info, send_task_fail_success_email
from core.configs import FUTURE_REDIS_DB

from future_market.models import (
    BaseEquity,
    SANDOQ_MARKET,
    GAVAHI_MARKET,
    CDC_MARKET,
    CONTRACT_CODE,
    ID,
)


redis_conn = RedisInterface(db=FUTURE_REDIS_DB)


NAME = "name"
INDEX = "index_col"
FILTER = "filter"
UNIQUE_IDENTIFIER = "unique_identifier"
SYMBOLS = "symbols"


def filter_sandoq_base_equities(all_funds: pd.DataFrame):
    filtered_funds = all_funds[~all_funds["Symbol"].str.contains(r"\d")]

    return filtered_funds


def filter_gavahi_base_equities(all_commodity: pd.DataFrame):
    filtered_commodity = all_commodity

    return filtered_commodity


def filter_cdc_base_equities(all_gold: pd.DataFrame):
    filtered_gold = all_gold

    return filtered_gold


BASE_EQUITY_KEYS = {
    #
    SANDOQ_MARKET: {
        NAME: "Name",
        INDEX: "Code",
        UNIQUE_IDENTIFIER: ID,
        FILTER: filter_sandoq_base_equities,
        SYMBOLS: {
            "LOTF": "ETC",  # LOTUS
            "ROBA": "KB",  # KAHROBA
            "JAVA": "JZ",  # JAVAHER
        },
    },
    #
    GAVAHI_MARKET: {
        NAME: "Name",
        INDEX: "Code",
        UNIQUE_IDENTIFIER: ID,
        FILTER: filter_gavahi_base_equities,
        SYMBOLS: {
            "IRK1A": "SAF",  # SAFFRON
            "IRK1K": "GC",  # GOLD COIN
        },
    },
    #
    CDC_MARKET: {
        NAME: "ContractDescription",
        INDEX: CONTRACT_CODE,
        UNIQUE_IDENTIFIER: CONTRACT_CODE,
        FILTER: filter_cdc_base_equities,
        SYMBOLS: {
            "CD1GOB": "GB",  # GOLD BAR
            "CD1SIB": "SIL",  # SILVER BAR
        },
    },
}


def update_base_equity_main():
    print(
        Fore.BLUE + "Updating base equity list for future market ..." + Style.RESET_ALL
    )
    for base_equity_key, properties in BASE_EQUITY_KEYS.items():
        try:
            data = redis_conn.client.get(name=base_equity_key)
            data = json.loads(data.decode("utf-8"))
            data = pd.DataFrame(data)
            data = (properties.get(FILTER))(data)
            symbols = properties.get(SYMBOLS)
            for index, symbol_code in symbols.items():
                symbol_rows = data[data[properties.get(INDEX)].str.contains(index)]
                symbol_rows = symbol_rows.to_dict(orient="records")
                for row in symbol_rows:
                    BaseEquity.objects.get_or_create(
                        base_equity_key=base_equity_key,
                        base_equity_name=row.get(properties.get(NAME)),
                        derivative_symbol=symbol_code,
                        unique_identifier=row.get(properties.get(UNIQUE_IDENTIFIER)),
                    )

        except Exception as e:
            print(Fore.RED)
            print(e)
            print(Style.RESET_ALL)
            continue

    print(
        Fore.GREEN + "All base equity list for future market updated" + Style.RESET_ALL
    )


def update_base_equity():
    TASK_NAME = update_base_equity.__name__
    print_task_info(name=TASK_NAME)

    try:
        update_base_equity_main()
        send_task_fail_success_email(task_name=TASK_NAME)
    except Exception as e:
        send_task_fail_success_email(task_name=TASK_NAME, exception=e)

    print_task_info(color="GREEN", name=TASK_NAME)
