import json
import pandas as pd
from celery import shared_task
from core.utils import RedisInterface, task_timing
from future_market.models import (
    BaseEquity,
    FUND_INFO,
    COMMODITY_INFO,
    GOLD_INFO,
    ID,
    CONTRACT_CODE,
    FUTURE_INFO,
)

redis_conn = RedisInterface(db=4)

BASE_EQUITY_SYMBOLS = {
    "زعفران": "SAF",
    "لوتوس": "ETC",
    "شمش": "GB",
    "كهربا": "KB",
}

UNIQUE_IDENTIFIER_COL = {
    FUND_INFO: ID,
    COMMODITY_INFO: ID,
    GOLD_INFO: CONTRACT_CODE,
    FUTURE_INFO: CONTRACT_CODE,
}


def get_base_equity_row(base_equity):
    base_equity_row = redis_conn.client.get(name=base_equity.base_equity_key)
    base_equity_row = json.loads(base_equity_row.decode("utf-8"))
    base_equity_row = pd.DataFrame(base_equity_row)
    base_equity_row = base_equity_row[
        base_equity_row[UNIQUE_IDENTIFIER_COL.get(base_equity.base_equity_key)]
        == base_equity.unique_identifier
    ]

    return base_equity_row


def get_future_derivatives(derivative_symbol):
    future_derivatives = redis_conn.client.get(name=FUTURE_INFO)
    future_derivatives = json.loads(future_derivatives.decode("utf-8"))
    future_derivatives = pd.DataFrame(future_derivatives)
    future_derivatives = future_derivatives[
        future_derivatives[UNIQUE_IDENTIFIER_COL.get(FUTURE_INFO)].str.contains(
            derivative_symbol, na=False
        )
    ]

    return future_derivatives


@task_timing
@shared_task(name="update_future_task")
def update_future():
    base_equities = BaseEquity.objects.all()
    for base_equity in base_equities:
        try:
            base_equity_row = get_base_equity_row(base_equity)
            future_derivatives = get_future_derivatives(base_equity.derivative_symbol)
            pass

        except Exception as e:
            print(e)
            continue
