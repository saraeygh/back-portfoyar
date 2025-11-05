from celery_singleton import Singleton

import pandas as pd

from colorama import Fore, Style

from samaneh.celery import app

from core.utils import MongodbInterface, run_main_task
from core.configs import FUTURE_MONGO_DB

from future_market.models import (
    OptionBaseEquity,
    SANDOQ_MARKET,
    GAVAHI_MARKET,
    CDC_MARKET,
    CONTRACT_CODE,
    ID,
)


NAME = "name"
INDEX = "index_col"
FILTER = "filter"
UNIQUE_IDENTIFIER = "unique_identifier"
SYMBOLS = "symbols"


def filter_sandoq_base_equities(all_funds: pd.DataFrame):
    if all_funds.empty:
        return all_funds

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
            "LOTF": ["TL", "FE"],  # LOTUS
            "ROBA": ["KB", "KA"],  # KAHROBA
            "JAVA": ["JZ"],  # JAVAHER
        },
    },
    #
    GAVAHI_MARKET: {
        NAME: "Name",
        INDEX: "Code",
        UNIQUE_IDENTIFIER: ID,
        FILTER: filter_gavahi_base_equities,
        SYMBOLS: {
            "IRK1A": ["SF", "FS"],  # SAFFRON
            "IRK1K": ["GC"],  # GOLD COIN
        },
    },
    #
    CDC_MARKET: {
        NAME: "ContractDescription",
        INDEX: CONTRACT_CODE,
        UNIQUE_IDENTIFIER: CONTRACT_CODE,
        FILTER: filter_cdc_base_equities,
        SYMBOLS: {
            "CD1GOB": ["GB"],  # GOLD BAR
        },
    },
}


def update_option_base_equity_main():
    print(
        Fore.BLUE + "Updating base equity list for future market ..." + Style.RESET_ALL
    )

    mongo_conn = MongodbInterface(db_name=FUTURE_MONGO_DB)
    for base_equity_key, properties in BASE_EQUITY_KEYS.items():
        mongo_conn.collection = mongo_conn.db[base_equity_key]
        data = pd.DataFrame(mongo_conn.collection.find({}, {"_id": 0}))
        if data.empty:
            continue
        data = (properties.get(FILTER))(data)
        symbols = properties.get(SYMBOLS)
        for index, symbol_codes in symbols.items():
            symbol_rows: pd.DataFrame = data[
                data[properties.get(INDEX)].str.contains(index)
            ]
            if symbol_rows.empty:
                continue

            symbol_rows = symbol_rows.to_dict(orient="records")
            for row in symbol_rows:
                for symbol_code in symbol_codes:
                    OptionBaseEquity.objects.get_or_create(
                        base_equity_key=base_equity_key,
                        base_equity_name=row.get(properties.get(NAME)),
                        derivative_symbol=symbol_code,
                        unique_identifier=row.get(properties.get(UNIQUE_IDENTIFIER)),
                    )

    print(
        Fore.GREEN + "All base equity list for future market updated" + Style.RESET_ALL
    )


@app.task(base=Singleton, name="update_option_base_equity_task")
def update_option_base_equity():

    run_main_task(
        main_task=update_option_base_equity_main,
        daily=True,
    )
