import json
from datetime import datetime

import pandas as pd
import jdatetime
from tqdm import tqdm

from core.utils import (
    RedisInterface,
    MONTHLY_INTEREST_RATE,
    MongodbInterface,
    get_deviation_percent,
    run_main_task,
)

from core.models import FeatureToggle
from core.configs import (
    HEZAR_RIAL_TO_BILLION_TOMAN,
    RIAL_TO_BILLION_TOMAN,
    FUTURE_REDIS_DB,
    FUTURE_MONGO_DB,
)
from future_market.models import (
    FutureBaseEquity,
    SANDOQ_MARKET,
    GAVAHI_MARKET,
    CDC_MARKET,
    ID,
    CONTRACT_CODE,
    FUTURE_MARKET,
)
from future_market.utils import RENAME_COLUMNS


UNIQUE_IDENTIFIER_COL = {
    SANDOQ_MARKET: ID,
    GAVAHI_MARKET: ID,
    CDC_MARKET: CONTRACT_CODE,
    FUTURE_MARKET: CONTRACT_CODE,
}


def get_base_equity_row(base_equity):
    mongo_conn = MongodbInterface(db_name=FUTURE_MONGO_DB)
    mongo_conn.collection = mongo_conn.db[base_equity.base_equity_key]

    base_equity_row = pd.DataFrame(mongo_conn.collection.find({}, {"_id": 0}))
    if base_equity_row.empty:
        return []

    base_equity_row = base_equity_row[
        base_equity_row[UNIQUE_IDENTIFIER_COL.get(base_equity.base_equity_key)]
        == base_equity.unique_identifier
    ]

    base_equity_row = base_equity_row.rename(
        columns=RENAME_COLUMNS.get(base_equity.base_equity_key)
    )
    base_equity_row = base_equity_row.to_dict(orient="records")

    if base_equity_row:
        return base_equity_row[0]
    return []


def get_future_derivatives(derivative_symbol):
    mongo_conn = MongodbInterface(db_name=FUTURE_MONGO_DB)
    mongo_conn.collection = mongo_conn.db[FUTURE_MARKET]
    future_derivatives = pd.DataFrame(mongo_conn.collection.find({}, {"_id": 0}))
    future_derivatives = future_derivatives[
        future_derivatives[UNIQUE_IDENTIFIER_COL.get(FUTURE_MARKET)].str.contains(
            derivative_symbol, na=False
        )
    ]

    future_derivatives = future_derivatives.rename(
        columns=RENAME_COLUMNS.get(FUTURE_MARKET)
    )
    future_derivatives = future_derivatives.to_dict(orient="records")

    return future_derivatives


def get_total_and_monthly_spread(
    open_position_price, base_equity_last_price, expiration, monthly_interest_rate
):
    spreads = []
    today_date = datetime.now().date()
    expiration_date = datetime.fromisoformat(expiration).date()
    remained_day = (expiration_date - today_date).days
    if remained_day < 1:
        return spreads

    total_spread = get_deviation_percent(open_position_price, base_equity_last_price)
    # monthly_spread = ((total_spread / remained_day) * 30) + monthly_interest_rate
    monthly_spread = (total_spread / remained_day) * 30

    spreads = {
        "total_spread": total_spread,
        "remained_day": remained_day,
        "monthly_spread": monthly_spread,
        "expiration_date": str(jdatetime.date.fromgregorian(date=expiration_date)),
    }

    return spreads


def long_future_result(
    base_equity_row: dict, future_derivatives: list, monthly_interest_rate: float
):
    base_equity_last_price = base_equity_row.get("close")
    if base_equity_last_price < 2:
        return []
    contract_size = base_equity_row.get("contract_size", 1)
    base_equity_last_price = base_equity_last_price * contract_size

    results = list()
    for row in future_derivatives:
        open_position_price = row.get("best_sell_price")
        if open_position_price < 2:
            continue
        expiration_date = row.get("expiration_date")
        spreads = get_total_and_monthly_spread(
            open_position_price,
            base_equity_last_price,
            expiration_date,
            monthly_interest_rate,
        )

        if spreads:
            result = {
                "derivative_name": row.get("name"),
                "best_sell_price": open_position_price,
                "derivative_value": row.get("trades_value")
                / HEZAR_RIAL_TO_BILLION_TOMAN,
                "derivative_last_update": row.get("last_update"),
                "base_equity_name": base_equity_row.get("name"),
                "base_equity_last_price": base_equity_last_price,
                "base_equity_value": base_equity_row.get("trades_value")
                / RIAL_TO_BILLION_TOMAN,
                "base_equity_last_update": base_equity_row.get("last_update"),
                **spreads,
                "initial_margin": row.get("initial_margin"),
                "open_interests": row.get("open_interests"),
                "last_settlement_price": row.get("last_settlement_price"),
                "today_settlement_price": row.get("today_settlement_price"),
                "contract_size": f"{row.get("contract_size")} {row.get("contract_size_unit_fa")}",
            }
            results.append(result)

    return results


def short_future_result(
    base_equity_row: list, future_derivatives: list, monthly_interest_rate: float
):
    base_equity_last_price = base_equity_row.get("close")
    if base_equity_last_price < 2:
        return []
    contract_size = base_equity_row.get("contract_size", 1)
    base_equity_last_price = base_equity_last_price * contract_size

    results = list()
    for row in future_derivatives:
        open_position_price = row.get("best_buy_price")
        if open_position_price < 2:
            continue
        expiration_date = row.get("expiration_date")
        spreads = get_total_and_monthly_spread(
            open_position_price,
            base_equity_last_price,
            expiration_date,
            -1 * monthly_interest_rate,
        )

        if spreads:
            result = {
                "derivative_name": row.get("name"),
                "best_buy_price": open_position_price,
                "derivative_value": row.get("trades_value")
                / HEZAR_RIAL_TO_BILLION_TOMAN,
                "derivative_last_update": row.get("last_update"),
                "base_equity_name": base_equity_row.get("name"),
                "base_equity_last_price": base_equity_last_price,
                "base_equity_value": base_equity_row.get("trades_value")
                / RIAL_TO_BILLION_TOMAN,
                "base_equity_last_update": base_equity_row.get("last_update"),
                **spreads,
                "initial_margin": row.get("initial_margin"),
                "open_interests": row.get("open_interests"),
                "last_settlement_price": row.get("last_settlement_price"),
                "today_settlement_price": row.get("today_settlement_price"),
                "contract_size": f"{row.get("contract_size")} {row.get("contract_size_unit_fa")}",
            }
            results.append(result)

    return results


def add_to_strategy_result(strategy_result, result):
    if isinstance(result, dict):
        strategy_result.append(result)
    elif isinstance(result, list):
        strategy_result = strategy_result + result

    return strategy_result


FUTURE_STRATEGIES = {
    "long_future": {
        "name": "لانگ",
        "calculate": long_future_result,
    },
    "short_future": {
        "name": "شورت",
        "calculate": short_future_result,
    },
}


def update_future_main():
    monthly_interest_rate = float(
        FeatureToggle.objects.get(name=MONTHLY_INTEREST_RATE["name"]).value
    )

    base_equities = FutureBaseEquity.objects.all()
    for strategy_key, properties in FUTURE_STRATEGIES.items():

        strategy_result = list()
        for base_equity in tqdm(base_equities, desc=f"{strategy_key} result", ncols=10):
            base_equity_row = get_base_equity_row(base_equity)

            if not base_equity_row:
                continue
            future_derivatives = get_future_derivatives(base_equity.derivative_symbol)

            calculate_result = properties.get("calculate")
            result = calculate_result(
                base_equity_row, future_derivatives, monthly_interest_rate
            )

            strategy_result = add_to_strategy_result(strategy_result, result)

        if strategy_result:
            mongo_conn = MongodbInterface(db_name=FUTURE_MONGO_DB)
            mongo_conn.collection = mongo_conn.db[strategy_key]
            mongo_conn.insert_docs_into_collection(strategy_result)


def update_future():

    run_main_task(
        main_task=update_future_main,
    )
