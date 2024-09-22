from django.shortcuts import get_object_or_404
import pandas as pd
from core.utils import RedisInterface
from option_market.models import OptionStrategy
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

RESULT_SORTING_COLUMN = "yearly_profit"


class StrategyResultAPIView(APIView):
    def get(self, request, strategy_key):
        get_object_or_404(OptionStrategy, key=strategy_key)
        strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
        return Response(strategy_result, status=status.HTTP_200_OK)


# NEW VIEW BASED ON RISK LEVELS #########################
def get_strategy_result_from_redis(strategy_key):
    strategy_result = RedisInterface(db=3)
    strategy_result = strategy_result.get_list_of_dicts(list_key=strategy_key)

    strategy_result = pd.DataFrame(strategy_result)
    try:
        strategy_result.sort_values(
            by=RESULT_SORTING_COLUMN, inplace=True, ascending=False
        )
    except KeyError:
        pass

    strategy_result = strategy_result.to_dict(orient="records")

    return strategy_result


# COVERED_CALL ##########################################
def get_low_risk_covered_call(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    if strategy_result:
        strategy_result = pd.DataFrame(strategy_result)
        strategy_result = strategy_result[
            strategy_result["strike_price"]
            <= 0.9 * strategy_result["base_equity_last_price"]
        ]

        try:
            strategy_result.sort_values(
                by=RESULT_SORTING_COLUMN, inplace=True, ascending=False
            )
        except KeyError:
            pass

        strategy_result = strategy_result.to_dict(orient="records")
    return strategy_result


def get_high_risk_covered_call(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    if strategy_result:
        strategy_result = pd.DataFrame(strategy_result)
        strategy_result = strategy_result[
            strategy_result["strike_price"]
            > 0.9 * strategy_result["base_equity_last_price"]
        ]

        try:
            strategy_result.sort_values(
                by=RESULT_SORTING_COLUMN, inplace=True, ascending=False
            )
        except KeyError:
            pass

        strategy_result = strategy_result.to_dict(orient="records")
    return strategy_result


# LONG_CALL ############################################
def get_higher_risk_roi_long_call(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    return strategy_result


# SHORT_CALL ###########################################
def get_low_risk_short_call(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    if strategy_result:
        strategy_result = pd.DataFrame(strategy_result)
        strategy_result = strategy_result[
            strategy_result["base_equity_last_price"]
            <= 0.9 * strategy_result["strike_price"]
        ]
        strategy_result = strategy_result.to_dict(orient="records")
    return strategy_result


def get_high_risk_short_call(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    if strategy_result:
        strategy_result = pd.DataFrame(strategy_result)
        strategy_result = strategy_result[
            strategy_result["base_equity_last_price"]
            > 0.9 * strategy_result["strike_price"]
        ]
        strategy_result = strategy_result.to_dict(orient="records")
    return strategy_result


# LONG_PUT #############################################
def get_high_risk_long_put(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    return strategy_result


# SHORT_PUT ############################################
def get_low_risk_short_put(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    if strategy_result:
        strategy_result = pd.DataFrame(strategy_result)
        strategy_result = strategy_result[
            strategy_result["strike_price"]
            <= 0.9 * strategy_result["base_equity_last_price"]
        ]
        strategy_result = strategy_result.to_dict(orient="records")
    return strategy_result


def get_high_risk_short_put(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    if strategy_result:
        strategy_result = pd.DataFrame(strategy_result)
        strategy_result = strategy_result[
            strategy_result["strike_price"]
            > 0.9 * strategy_result["base_equity_last_price"]
        ]
        strategy_result = strategy_result.to_dict(orient="records")
    return strategy_result


# LONG_STRADDLE #######################################
def get_higher_risk_roi_long_straddle(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    return strategy_result


# SHORT_STRADDLE #######################################
def get_high_risk_short_straddle(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    return strategy_result


# BULL_CALL_SPREAD ############################################
def get_low_risk_bull_call_spread(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    if strategy_result:
        strategy_result = pd.DataFrame(strategy_result)
        strategy_result = strategy_result[
            strategy_result["call_sell_strike"]
            < strategy_result["base_equity_last_price"]
        ]
        strategy_result = strategy_result.to_dict(orient="records")
    return strategy_result


def get_high_risk_bull_call_spread(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    if strategy_result:
        strategy_result = pd.DataFrame(strategy_result)
        strategy_result = strategy_result[
            strategy_result["call_buy_strike"]
            > strategy_result["base_equity_last_price"]
        ]
        strategy_result = strategy_result.to_dict(orient="records")
    return strategy_result


# BEAR_CALL_SPREAD #######################################
def get_high_risk_bear_call_spread(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    return strategy_result


# BULL_PUT_SPREAD #######################################
def get_low_risk_bull_put_spread(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    return strategy_result


# BEAR_PUT_SPREAD #######################################
def get_high_risk_bear_put_spread(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    return strategy_result


# LONG_STRANGLE ############################################
def get_lower_risk_long_strangle(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    if strategy_result:
        strategy_result = pd.DataFrame(strategy_result)
        strategy_result = strategy_result[
            strategy_result["call_buy_strike"]
            < strategy_result["base_equity_last_price"]
        ]
        strategy_result = strategy_result.to_dict(orient="records")
    return strategy_result


def get_higher_risk_roi_long_strangle(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    if strategy_result:
        strategy_result = pd.DataFrame(strategy_result)
        strategy_result = strategy_result[
            strategy_result["call_buy_strike"]
            > strategy_result["base_equity_last_price"]
        ]
        strategy_result = strategy_result.to_dict(orient="records")
    return strategy_result


# SHORT_STRANGLE #######################################
def get_high_risk_short_strangle(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    return strategy_result


# LONG_BUTTERFLY #######################################
def get_high_risk_long_butterfly(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    return strategy_result


# SHORT_BUTTERFLY #######################################
def get_high_risk_short_butterfly(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    return strategy_result


# COLLAR ############################################
def get_low_risk_collar(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    if strategy_result:
        strategy_result = pd.DataFrame(strategy_result)
        strategy_result = strategy_result[
            strategy_result["call_buy_strike_high"]
            < strategy_result["base_equity_last_price"]
        ]
        strategy_result = strategy_result.to_dict(orient="records")
    return strategy_result


def get_higher_risk_roi_collar(strategy_key):
    strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
    if strategy_result:
        strategy_result = pd.DataFrame(strategy_result)
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
    # LONG_CALL
    "higher_risk_roi_long_call": get_higher_risk_roi_long_call,
    # SHORT_CALL
    "low_risk_short_call": get_low_risk_short_call,
    "high_risk_short_call": get_high_risk_short_call,
    # LONG_PUT
    "high_risk_long_put": get_high_risk_long_put,
    # SHORT_PUT
    "low_risk_short_put": get_low_risk_short_put,
    "high_risk_short_put": get_high_risk_short_put,
    # LONG_STRADDLE
    "higher_risk_roi_long_straddle": get_higher_risk_roi_long_straddle,
    # SHORT_STRADDLE
    "high_risk_short_straddle": get_high_risk_short_straddle,
    # BULL_CALL_SPREAD
    "low_risk_bull_call_spread": get_low_risk_bull_call_spread,
    "high_risk_bull_call_spread": get_high_risk_bull_call_spread,
    # BEAR_CALL_SPREAD
    "high_risk_bear_call_spread": get_high_risk_bear_call_spread,
    # BULL_PUT_SPREAD
    "low_risk_bull_put_spread": get_low_risk_bull_put_spread,
    # BEAR_PUT_SPREAD
    "high_risk_bear_put_spread": get_high_risk_bear_put_spread,
    # LONG_STRANGLE
    "lower_risk_long_strangle": get_lower_risk_long_strangle,
    "higher_risk_roi_long_strangle": get_higher_risk_roi_long_strangle,
    # SHORT_STRANGLE
    "high_risk_short_strangle": get_high_risk_short_strangle,
    # LONG_BUTTERFLY
    "high_risk_long_butterfly": get_high_risk_long_butterfly,
    # SHORT_BUTTERFLY
    "high_risk_short_butterfly": get_high_risk_short_butterfly,
    # COLLAR
    "lower_risk_collar": get_low_risk_collar,
    "higher_risk_roi_collar": get_higher_risk_roi_collar,
}


class PositionsAPIView(APIView):
    def get(self, request, risk_level: str, strategy_key):

        if risk_level.startswith("all_risk"):
            strategy_result = get_strategy_result_from_redis(strategy_key=strategy_key)
        else:
            filter_key = f"{risk_level}_{strategy_key}"
            strategy_result = (FILTER_DICT.get(filter_key))(strategy_key)

        return Response(strategy_result, status=status.HTTP_200_OK)
