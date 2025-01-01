import pandas as pd

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from core.configs import OPTION_REDIS_DB
from core.utils import (
    RedisInterface,
    TABLE_COLS_QP,
    ALL_TABLE_COLS,
    STRATEGIES,
    SUMMARY_TABLE_COLS,
)

from option_market.permissions import HasOptionSubscription

PROFIT_SORTING_COLUMN = "monthly_profit"
BREAK_EVEN_SORTING_COLUMN = "monthly_break_even"

redis_conn = RedisInterface(db=OPTION_REDIS_DB)


def drop_unwanted_cols(strategy_result: pd.DataFrame, strategy_key: str):
    if strategy_result.empty:
        return strategy_result

    strategy_result.drop(STRATEGIES[strategy_key]["drop_cols"], axis=1, inplace=True)
    return strategy_result


def sort_strategy_result(strategy_result_df, sort_column: str = PROFIT_SORTING_COLUMN):
    try:
        strategy_result_df.sort_values(by=sort_column, inplace=True, ascending=False)
        return strategy_result_df
    except Exception:
        pass

    try:
        strategy_result_df.sort_values(
            by=BREAK_EVEN_SORTING_COLUMN, inplace=True, ascending=False
        )
        return strategy_result_df
    except Exception:
        return strategy_result_df


# NEW VIEW BASED ON RISK LEVELS #########################
def get_strategy_result_from_redis(strategy_key, table=None):
    strategy_result = redis_conn.get_list_of_dicts(list_key=strategy_key)

    strategy_result = pd.DataFrame(strategy_result)
    if table == ALL_TABLE_COLS:
        pass
    else:
        strategy_result = drop_unwanted_cols(strategy_result, strategy_key)

    strategy_result = sort_strategy_result(strategy_result)

    return strategy_result


# COVERED_CALL ##########################################
def get_low_risk_covered_call(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    if not strategy_result.empty:
        strategy_result = strategy_result[
            strategy_result["strike_price"] <= strategy_result["base_equity_last_price"]
        ]
    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


def get_high_risk_covered_call(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    if not strategy_result.empty:
        strategy_result = strategy_result[
            (
                1.15 * strategy_result["base_equity_last_price"]
                >= strategy_result["strike_price"]
            )
            & (
                strategy_result["strike_price"]
                > strategy_result["base_equity_last_price"]
            )
        ]

    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


# CONVERSION ############################################
def get_no_risk_conversion(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)

    if not strategy_result.empty:
        strategy_result = strategy_result[strategy_result[PROFIT_SORTING_COLUMN] >= 0]

    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


# LONG_CALL ############################################
def get_high_risk_long_call(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    strategy_result = strategy_result.to_dict(orient="records")
    return strategy_result


# SHORT_CALL ###########################################
def get_low_risk_short_call(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    if not strategy_result.empty:
        strategy_result = strategy_result[
            strategy_result["base_equity_last_price"] <= strategy_result["strike_price"]
        ]
    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


def get_high_risk_short_call(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    if not strategy_result.empty:
        strategy_result = strategy_result[
            strategy_result["base_equity_last_price"] > strategy_result["strike_price"]
        ]
    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


# LONG_PUT #############################################
def get_high_risk_long_put(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    strategy_result = strategy_result.to_dict(orient="records")
    return strategy_result


# SHORT_PUT ############################################
def get_high_risk_short_put(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    if not strategy_result.empty:
        strategy_result = strategy_result[
            strategy_result["strike_price"] > strategy_result["base_equity_last_price"]
        ]
    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


# LONG_STRADDLE #######################################
def get_high_risk_long_straddle(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


# SHORT_STRADDLE #######################################
def get_high_risk_short_straddle(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


# BULL_CALL_SPREAD ############################################
def get_low_risk_bull_call_spread(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    if not strategy_result.empty:
        strategy_result = strategy_result[
            strategy_result["call_sell_strike"]
            < strategy_result["base_equity_last_price"]
        ]
    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


def get_high_risk_bull_call_spread(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    if not strategy_result.empty:
        strategy_result = strategy_result[
            strategy_result["call_buy_strike"]
            > strategy_result["base_equity_last_price"]
        ]
    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


# BEAR_CALL_SPREAD #######################################
def get_high_risk_bear_call_spread(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


# BULL_PUT_SPREAD #######################################
def get_low_risk_bull_put_spread(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


def get_high_risk_bull_put_spread(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    if not strategy_result.empty:
        strategy_result = strategy_result[
            strategy_result["put_sell_strike"]
            > strategy_result["base_equity_last_price"]
        ]
    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


# BEAR_PUT_SPREAD #######################################
def get_low_risk_bear_put_spread(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    if not strategy_result.empty:
        strategy_result = strategy_result[
            strategy_result["put_sell_strike"]
            > strategy_result["base_equity_last_price"]
        ]
    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


def get_high_risk_bear_put_spread(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


# LONG_STRANGLE ############################################
def get_low_risk_long_strangle(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    if not strategy_result.empty:
        strategy_result = strategy_result[
            strategy_result["call_buy_strike"]
            < strategy_result["base_equity_last_price"]
        ]
    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


def get_high_risk_long_strangle(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    if not strategy_result.empty:
        strategy_result = strategy_result[
            strategy_result["call_buy_strike"]
            > strategy_result["base_equity_last_price"]
        ]
    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


# SHORT_STRANGLE #######################################
def get_high_risk_short_strangle(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


# LONG_BUTTERFLY #######################################
def get_high_risk_long_butterfly(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


# SHORT_BUTTERFLY #######################################
def get_high_risk_short_butterfly(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


# COLLAR ############################################
def get_low_risk_collar(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    if not strategy_result.empty:
        strategy_result = strategy_result[
            strategy_result["call_buy_strike_high"]
            < strategy_result["base_equity_last_price"]
        ]
    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


def get_high_risk_collar(strategy_key, table=None):
    strategy_result = get_strategy_result_from_redis(strategy_key, table)
    if not strategy_result.empty:
        strategy_result = strategy_result[
            strategy_result["call_buy_strike_high"]
            > strategy_result["base_equity_last_price"]
        ]
    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


FILTER_DICT = {
    # COVERED_CALL
    "low_risk_covered_call": get_low_risk_covered_call,
    "high_risk_covered_call": get_high_risk_covered_call,
    # CONVERSION
    "no_risk_conversion": get_no_risk_conversion,
    # LONG_CALL
    "high_risk_long_call": get_high_risk_long_call,
    # SHORT_CALL
    "low_risk_short_call": get_low_risk_short_call,
    "high_risk_short_call": get_high_risk_short_call,
    # LONG_PUT
    "high_risk_long_put": get_high_risk_long_put,
    # SHORT_PUT
    "high_risk_short_put": get_high_risk_short_put,
    # LONG_STRADDLE
    "high_risk_long_straddle": get_high_risk_long_straddle,
    # SHORT_STRADDLE
    "high_risk_short_straddle": get_high_risk_short_straddle,
    # BULL_CALL_SPREAD
    "low_risk_bull_call_spread": get_low_risk_bull_call_spread,
    "high_risk_bull_call_spread": get_high_risk_bull_call_spread,
    # BEAR_CALL_SPREAD
    "high_risk_bear_call_spread": get_high_risk_bear_call_spread,
    # BULL_PUT_SPREAD
    "low_risk_bull_put_spread": get_low_risk_bull_put_spread,
    "high_risk_bull_put_spread": get_high_risk_bull_put_spread,
    # BEAR_PUT_SPREAD
    "low_risk_bear_put_spread": get_low_risk_bear_put_spread,
    "high_risk_bear_put_spread": get_high_risk_bear_put_spread,
    # LONG_STRANGLE
    "low_risk_long_strangle": get_low_risk_long_strangle,
    "high_risk_long_strangle": get_high_risk_long_strangle,
    # SHORT_STRANGLE
    "high_risk_short_strangle": get_high_risk_short_strangle,
    # LONG_BUTTERFLY
    "high_risk_long_butterfly": get_high_risk_long_butterfly,
    # SHORT_BUTTERFLY
    "high_risk_short_butterfly": get_high_risk_short_butterfly,
    # COLLAR
    "low_risk_collar": get_low_risk_collar,
    "high_risk_collar": get_high_risk_collar,
}


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasOptionSubscription])
class OptionPositionsAPIView(APIView):
    def get(self, request, risk_level: str, strategy_key: str):

        table = request.query_params.get(TABLE_COLS_QP, SUMMARY_TABLE_COLS)
        if risk_level == "all_risk":
            strategy_result = get_strategy_result_from_redis(strategy_key, table)
            strategy_result = strategy_result.to_dict(orient="records")
        else:
            filter_key = f"{risk_level}_{strategy_key}"
            strategy_result = (FILTER_DICT.get(filter_key))(strategy_key, table)

        return Response(strategy_result, status=status.HTTP_200_OK)
