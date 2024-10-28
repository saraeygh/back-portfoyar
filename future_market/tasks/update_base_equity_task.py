import json
import pandas as pd
from celery import shared_task
from core.configs import FUTURE_REDIS_DB
from core.utils import RedisInterface, task_timing
from future_market.models import (
    BaseEquity,
    FUND_INFO,
    COMMODITY_INFO,
    GOLD_INFO,
    ID,
    CONTRACT_CODE,
)
from colorama import Fore, Style

redis_conn = RedisInterface(db=FUTURE_REDIS_DB)

BASE_EQUITY_SYMBOLS = {
    "زعفران": "SAF",
    "لوتوس": "ETC",
    "شمش": "GB",
    "كهربا": "KB",
}

NAME_COL = "name"
FILTER_BASE_EQUITIES = "filter"
UNIQUE_IDENTIFIER_COL = "unique_identifier"


def filter_fund_base_equities(all_funds: pd.DataFrame):
    filtered_funds = all_funds[~all_funds["Symbol"].str.contains(r"\d")]
    filtered_funds = filtered_funds.to_dict(orient="records")

    return filtered_funds


def filter_commodity_base_equities(all_commodity: pd.DataFrame):
    filtered_commodity = all_commodity
    filtered_commodity = filtered_commodity.to_dict(orient="records")
    return filtered_commodity


def filter_gold_base_equities(all_gold: pd.DataFrame):
    filtered_gold = all_gold
    filtered_gold = filtered_gold.to_dict(orient="records")
    return filtered_gold


BASE_EQUITY_KEYS = {
    FUND_INFO: {
        NAME_COL: "Name",
        UNIQUE_IDENTIFIER_COL: ID,
        FILTER_BASE_EQUITIES: filter_fund_base_equities,
    },
    COMMODITY_INFO: {
        NAME_COL: "Name",
        UNIQUE_IDENTIFIER_COL: ID,
        FILTER_BASE_EQUITIES: filter_commodity_base_equities,
    },
    GOLD_INFO: {
        NAME_COL: "ContractDescription",
        UNIQUE_IDENTIFIER_COL: CONTRACT_CODE,
        FILTER_BASE_EQUITIES: filter_gold_base_equities,
    },
}

TO_BE_DELETED = {
    "SAF": "51200575796028449",
}


@task_timing
@shared_task(name="update_base_equity_task")
def update_base_equity():
    print(
        Fore.BLUE + "Updating base equity list for future market ..." + Style.RESET_ALL
    )
    for name, symbol in BASE_EQUITY_SYMBOLS.items():
        for base_equity_key, properties in BASE_EQUITY_KEYS.items():
            try:
                data = redis_conn.client.get(name=base_equity_key)
                data = json.loads(data.decode("utf-8"))
                data = pd.DataFrame(data)
                data = (properties.get(FILTER_BASE_EQUITIES))(data)
                for datum in data:
                    base_equity_name = datum.get(properties.get(NAME_COL))
                    if name in base_equity_name:
                        base_equity = BaseEquity.objects.filter(
                            base_equity_key=base_equity_key,
                            base_equity_name=base_equity_name,
                            derivative_symbol=symbol,
                            unique_identifier=datum.get(
                                properties.get(UNIQUE_IDENTIFIER_COL)
                            ),
                        )
                        if not base_equity.exists():
                            BaseEquity.objects.create(
                                base_equity_key=base_equity_key,
                                base_equity_name=base_equity_name,
                                derivative_symbol=symbol,
                                unique_identifier=datum.get(
                                    properties.get(UNIQUE_IDENTIFIER_COL)
                                ),
                            )
            except Exception as e:
                print(Fore.RED)
                print(e)
                print(Style.RESET_ALL)
                continue
    print(
        Fore.GREEN + "All base equity list for future market updated" + Style.RESET_ALL
    )

    print(Fore.BLUE + "Deleting mistaken base equities ..." + Style.RESET_ALL)

    for derivative_symbol, unique_identifier in TO_BE_DELETED.items():
        try:
            base_equities = BaseEquity.objects.filter(
                derivative_symbol=derivative_symbol, unique_identifier=unique_identifier
            )
            base_equities.delete()
        except BaseEquity.DoesNotExist:
            continue
        except Exception as e:
            print(Fore.RED)
            print(e)
            print(Style.RESET_ALL)
            continue

    print(Fore.GREEN + "Mistaken base equities deleted" + Style.RESET_ALL)
