import json
import pandas as pd
from core.utils import (
    RedisInterface,
    MONTHLY_INTEREST_RATE,
    get_deviation_percent,
    print_task_info,
)

from core.models import FeatureToggle
from core.configs import (
    HEZAR_RIAL_TO_BILLION_TOMAN,
    RIAL_TO_BILLION_TOMAN,
    FUTURE_REDIS_DB,
)
from future_market.models import (
    BaseEquity,
    FUND_INFO,
    COMMODITY_INFO,
    GOLD_INFO,
    ID,
    CONTRACT_CODE,
    FUTURE_INFO,
)
from future_market.utils import RENAME_COLUMNS
from datetime import datetime
import jdatetime
from tqdm import tqdm

redis_conn = RedisInterface(db=FUTURE_REDIS_DB)

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

    base_equity_row = base_equity_row.rename(
        columns=RENAME_COLUMNS.get(base_equity.base_equity_key)
    )
    base_equity_row = base_equity_row.to_dict(orient="records")

    return base_equity_row[0]


def get_future_derivatives(derivative_symbol):
    future_derivatives = redis_conn.client.get(name=FUTURE_INFO)
    future_derivatives = json.loads(future_derivatives.decode("utf-8"))
    future_derivatives = pd.DataFrame(future_derivatives)
    future_derivatives = future_derivatives[
        future_derivatives[UNIQUE_IDENTIFIER_COL.get(FUTURE_INFO)].str.contains(
            derivative_symbol, na=False
        )
    ]

    future_derivatives = future_derivatives.rename(
        columns=RENAME_COLUMNS.get(FUTURE_INFO)
    )
    future_derivatives = future_derivatives.to_dict(orient="records")

    return future_derivatives


def get_total_and_monthly_spread(
    open_position_price, base_equity_last_price, expiration, monthly_interest_rate
):
    try:
        total_spread = get_deviation_percent(
            open_position_price, base_equity_last_price
        )
        expiration_date = datetime.fromisoformat(expiration).date()
        today_date = datetime.now().date()
        remained_day = (expiration_date - today_date).days
        monthly_spread = ((total_spread / remained_day) * 30) + monthly_interest_rate
        spreads = {
            "total_spread": total_spread,
            "remained_day": remained_day,
            "monthly_spread": monthly_spread,
            "expiration_date": str(jdatetime.date.fromgregorian(date=expiration_date)),
        }
        return spreads

    except Exception:
        return None


def long_future_result(
    base_equity_row: dict, future_derivatives: list, monthly_interest_rate: float
):
    base_equity_last_price = base_equity_row.get("close")
    if base_equity_last_price == 0:
        return []
    contract_size = base_equity_row.get("contract_size", 1)
    base_equity_last_price = base_equity_last_price * contract_size

    results = list()
    for row in future_derivatives:
        open_position_price = row.get("best_sell_price")
        if open_position_price == 0:
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
    if base_equity_last_price == 0:
        return []
    contract_size = base_equity_row.get("contract_size", 1)
    base_equity_last_price = base_equity_last_price * contract_size

    results = list()
    for row in future_derivatives:
        open_position_price = row.get("best_buy_price")
        if open_position_price == 0:
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
        "name": "موقعیت لانگ",
        "calculate": long_future_result,
    },
    "short_future": {
        "name": "موقعیت شورت",
        "calculate": short_future_result,
    },
}


def update_future_main():
    try:
        monthly_interest_rate = FeatureToggle.objects.get(
            name=MONTHLY_INTEREST_RATE["name"]
        )
        monthly_interest_rate = float(monthly_interest_rate.value)
    except Exception:
        monthly_interest_rate = 0

    base_equities = BaseEquity.objects.all()
    for strategy_key, properties in FUTURE_STRATEGIES.items():

        strategy_result = list()
        for base_equity in tqdm(base_equities, desc=f"{strategy_key} result", ncols=10):
            try:
                base_equity_row = get_base_equity_row(base_equity)
                future_derivatives = get_future_derivatives(
                    base_equity.derivative_symbol
                )

                calculate_result = properties.get("calculate")
                result = calculate_result(
                    base_equity_row, future_derivatives, monthly_interest_rate
                )

                strategy_result = add_to_strategy_result(strategy_result, result)

            except Exception:
                continue

        if strategy_result:
            serialized_data = json.dumps(strategy_result)
            redis_conn.client.set(strategy_key, serialized_data)


def update_future():
    print_task_info(name=__name__)

    update_future_main()

    print_task_info(color="GREEN", name=__name__)
