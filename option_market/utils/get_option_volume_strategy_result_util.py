from core.configs import OPTION_DB

import re

import pandas as pd
from core.utils import MongodbInterface

from . import match_strategy_for_single_symbol


def prepare_history_data_for_strategy(symbol: str):
    mongodb_conn = MongodbInterface(db_name=OPTION_DB, collection_name="history")
    query_filter = {"option_symbol": symbol}
    symbol_history = mongodb_conn.collection.find_one(query_filter, {"_id": 0})
    symbol_history = symbol_history["history"]

    symbol_history_df = pd.DataFrame(symbol_history)
    asset_name = symbol_history_df["asset_name"].iloc[0]
    symbol_history_df = symbol_history_df.drop(
        symbol_history_df[symbol_history_df["volume"] == 0].index
    )

    symbol_history_df = symbol_history_df.drop(
        symbol_history_df[symbol_history_df["close_price"] == 0].index
    )

    symbol_history_df.dropna(inplace=True)

    symbol_history_df = symbol_history_df.iloc[::-1]

    symbol_history_df.reset_index(drop=True, inplace=True)

    return symbol_history_df, asset_name


def evaluate_strategy_result(
    volume_change_ratio,
    return_period,
    threshold,
    on_change_total_matched_threshold_count,
    after_change_total_matched_threshold_count,
    total_matched_strategy_count,
    on_change_mean_of_max_comulative_return_percent_list,
    after_change_mean_of_max_comulative_return_percent_list,
    on_change_day_to_max_comulative_return_percent_list,
    after_change_day_to_max_comulative_return_percent_list,
    asset_name,
    option_symbol_alphabet,
):
    if total_matched_strategy_count != 0:
        on_change_win_rate = (
            on_change_total_matched_threshold_count / total_matched_strategy_count
        ) * 100
        after_change_win_rate = (
            after_change_total_matched_threshold_count / total_matched_strategy_count
        ) * 100
    else:
        on_change_win_rate = None
        after_change_win_rate = None
    ###########################################################################
    if on_change_mean_of_max_comulative_return_percent_list:
        on_change_max_possible_return_percent = sum(
            on_change_mean_of_max_comulative_return_percent_list
        ) / len(on_change_mean_of_max_comulative_return_percent_list)
    else:
        on_change_max_possible_return_percent = None

    if on_change_day_to_max_comulative_return_percent_list:
        on_change_expected_day_of_max_return_percent = sum(
            on_change_day_to_max_comulative_return_percent_list
        ) / len(on_change_day_to_max_comulative_return_percent_list)
    else:
        on_change_expected_day_of_max_return_percent = None
    ###########################################################################
    if after_change_mean_of_max_comulative_return_percent_list:
        after_change_max_possible_return_percent = sum(
            after_change_mean_of_max_comulative_return_percent_list
        ) / len(after_change_mean_of_max_comulative_return_percent_list)
    else:
        after_change_max_possible_return_percent = None

    if after_change_day_to_max_comulative_return_percent_list:
        after_change_expected_day_of_max_return_percent = sum(
            after_change_day_to_max_comulative_return_percent_list
        ) / len(after_change_day_to_max_comulative_return_percent_list)
    else:
        after_change_expected_day_of_max_return_percent = None
    ###########################################################################
    if (
        on_change_win_rate is not None
        and on_change_max_possible_return_percent is not None
        and on_change_expected_day_of_max_return_percent is not None
        and after_change_win_rate is not None
        and after_change_max_possible_return_percent is not None
        and after_change_expected_day_of_max_return_percent is not None
    ):
        strategy_result = {
            "asset_name": asset_name,
            "option_group": option_symbol_alphabet,
            "volume_change_ratio": volume_change_ratio,
            "return_period": return_period,
            "threshold": threshold,
            "on_change_win_rate": on_change_win_rate,
            "on_change_max_possible_return_percent": on_change_max_possible_return_percent,
            "on_change_expected_day_of_max_return_percent": on_change_expected_day_of_max_return_percent,
            "after_change_win_rate": after_change_win_rate,
            "after_change_max_possible_return_percent": after_change_max_possible_return_percent,
            "after_change_expected_day_of_max_return_percent": after_change_expected_day_of_max_return_percent,
        }
    else:
        strategy_result = {}

    return strategy_result


def save_strategy_result_list(
    strategy_result_list,
    volume_change_ratio,
    return_period,
    threshold,
):
    result_key = f"m_{volume_change_ratio}_d_{return_period}_t_{threshold}"

    mongodb_conn = MongodbInterface(
        db_name=OPTION_DB, collection_name="option_volume_strategy_result"
    )

    query_filter = {"result_key": result_key}
    mongodb_conn.collection.delete_one(query_filter)

    mongodb_conn.collection.insert_one(
        {"result_key": result_key, "result": strategy_result_list}
    )

    return


def get_option_volume_strategy_result(
    volume_change_ratio: int, return_period: int, threshold: int
):
    mongodb_conn = MongodbInterface(db_name=OPTION_DB, collection_name="history")
    option_symbols = list(
        mongodb_conn.collection.find({}, {"_id": 0, "option_symbol": 1})
    )
    option_symbols = set(option["option_symbol"] for option in option_symbols)

    DIGITS_REGEX = r"[0-9]"
    strategy_result_list = []
    while_loop_limitation = len(option_symbols)
    while while_loop_limitation > 0 and len(option_symbols) > 0:
        while_loop_limitation -= 1

        option_symbol = option_symbols.pop()
        option_symbol_alphabet = re.sub(DIGITS_REGEX, "", option_symbol)
        all_similar_option_symbols = {
            option_symbol
            for option_symbol in option_symbols
            if option_symbol_alphabet in option_symbol
        }
        option_symbols = option_symbols - all_similar_option_symbols

        on_change_total_matched_threshold_count = 0
        after_change_total_matched_threshold_count = 0
        total_matched_strategy_count = 0
        on_change_mean_of_max_comulative_return_percent_list = []
        on_change_day_to_max_comulative_return_percent_list = []

        after_change_mean_of_max_comulative_return_percent_list = []
        after_change_day_to_max_comulative_return_percent_list = []

        for symbol in all_similar_option_symbols:
            symbol_history_df, asset_name = prepare_history_data_for_strategy(
                symbol=symbol
            )

            (
                matched_strategy_list,
                on_change_matched_threshold_count,
                on_change_mean_of_max_comulative_return_percent_list,
                on_change_day_to_max_return_percent_list,
                after_change_matched_threshold_count,
                after_change_mean_of_max_comulative_return_percent_list,
                after_change_day_to_max_return_percent_list,
            ) = match_strategy_for_single_symbol(
                symbol_history_df=symbol_history_df,
                on_change_mean_of_max_comulative_return_percent_list=on_change_mean_of_max_comulative_return_percent_list,
                on_change_day_to_max_return_percent_list=on_change_day_to_max_comulative_return_percent_list,
                after_change_mean_of_max_comulative_return_percent_list=after_change_mean_of_max_comulative_return_percent_list,
                after_change_day_to_max_return_percent_list=after_change_day_to_max_comulative_return_percent_list,
                volume_change_ratio=volume_change_ratio,
                return_period=return_period,
                threshold=threshold,
            )

            on_change_total_matched_threshold_count += on_change_matched_threshold_count
            after_change_total_matched_threshold_count += (
                after_change_matched_threshold_count
            )

            total_matched_strategy_count += len(matched_strategy_list)

        strategy_result = evaluate_strategy_result(
            volume_change_ratio=volume_change_ratio,
            return_period=return_period,
            threshold=threshold,
            on_change_total_matched_threshold_count=on_change_total_matched_threshold_count,
            after_change_total_matched_threshold_count=after_change_total_matched_threshold_count,
            total_matched_strategy_count=total_matched_strategy_count,
            on_change_mean_of_max_comulative_return_percent_list=on_change_mean_of_max_comulative_return_percent_list,
            after_change_mean_of_max_comulative_return_percent_list=after_change_mean_of_max_comulative_return_percent_list,
            on_change_day_to_max_comulative_return_percent_list=on_change_day_to_max_return_percent_list,
            after_change_day_to_max_comulative_return_percent_list=after_change_day_to_max_return_percent_list,
            asset_name=asset_name,
            option_symbol_alphabet=option_symbol_alphabet,
        )

        if strategy_result:
            strategy_result_list.append(strategy_result)

    if strategy_result_list:
        save_strategy_result_list(
            strategy_result_list=strategy_result_list,
            volume_change_ratio=volume_change_ratio,
            return_period=return_period,
            threshold=threshold,
        )
