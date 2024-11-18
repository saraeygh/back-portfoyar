from core.configs import OPTION_MONGO_DB
import pandas as pd
from core.utils import MongodbInterface


def add_on_change_max_comulative_return_percent(row):
    on_change_comulative_return_percent_list = row[
        "on_change_comulative_return_percent_list"
    ]

    if on_change_comulative_return_percent_list:
        on_change_max_comulative_return_percent = max(
            on_change_comulative_return_percent_list
        )

        return on_change_max_comulative_return_percent

    return None


def add_after_change_max_comulative_return_percent(row):
    after_change_comulative_return_percent_list = row[
        "after_change_comulative_return_percent_list"
    ]

    if after_change_comulative_return_percent_list:
        after_change_max_comulative_return_percent = max(
            after_change_comulative_return_percent_list
        )

        return after_change_max_comulative_return_percent

    return None


def add_on_change_day_of_max_percent(row):
    on_change_max_comulative_return_percent = row[
        "on_change_max_comulative_return_percent"
    ]
    on_change_comulative_return_percent_list = row[
        "on_change_comulative_return_percent_list"
    ]
    if (
        on_change_comulative_return_percent_list
        and on_change_max_comulative_return_percent is not None
    ):
        try:
            on_change_day_of_max_percent = (
                on_change_comulative_return_percent_list.index(
                    on_change_max_comulative_return_percent
                )
            ) + 1
            return on_change_day_of_max_percent
        except ValueError:
            return None

    return None


def add_after_change_day_of_max_percent(row):
    after_change_max_comulative_return_percent = row[
        "after_change_max_comulative_return_percent"
    ]
    after_change_comulative_return_percent_list = row[
        "after_change_comulative_return_percent_list"
    ]
    if (
        after_change_comulative_return_percent_list
        and after_change_max_comulative_return_percent is not None
    ):
        try:
            after_change_day_of_max_percent = (
                after_change_comulative_return_percent_list.index(
                    after_change_max_comulative_return_percent
                )
            ) + 1
            return after_change_day_of_max_percent
        except ValueError:
            return None

    return None


def add_on_change_day_of_pass_threshold(row, threshold):
    on_change_comulative_return_percent_list = row[
        "on_change_comulative_return_percent_list"
    ]

    if on_change_comulative_return_percent_list:
        for index, comulative_return_percent in enumerate(
            on_change_comulative_return_percent_list
        ):
            if comulative_return_percent > threshold:
                day_of_pass_threshold = index + 1
                return day_of_pass_threshold

    return 0


def add_after_change_day_of_pass_threshold(row, threshold):
    after_change_comulative_return_percent_list = row[
        "after_change_comulative_return_percent_list"
    ]

    if after_change_comulative_return_percent_list:
        for index, comulative_return_percent in enumerate(
            after_change_comulative_return_percent_list
        ):
            if comulative_return_percent > threshold:
                day_of_pass_threshold = index + 1
                return day_of_pass_threshold

    return 0


def match_strategy_for_single_symbol(
    symbol_history_df: pd.DataFrame,
    on_change_mean_of_max_comulative_return_percent_list: list,
    on_change_day_to_max_return_percent_list: list,
    after_change_mean_of_max_comulative_return_percent_list: list,
    after_change_day_to_max_return_percent_list: list,
    volume_change_ratio: int,
    return_period: int,
    threshold: int = 0,
) -> tuple:
    mongodb_conn = MongodbInterface(
        db_name=OPTION_MONGO_DB, collection_name="one_year_total_volumes"
    )

    df_last_index = symbol_history_df.shape[0] - 1
    on_change_matched_threshold_count = 0
    after_change_matched_threshold_count = 0
    matched_strategy_list = []
    prevent_repeated_strategy_list = []
    for current_day_index, current_row_data in symbol_history_df.iterrows():
        VALID_CHANGE_FLAG = True
        change_day_index = current_day_index + 1
        after_change_day_index = change_day_index + 1

        if after_change_day_index + 1 > df_last_index:
            break

        current_day_volume = symbol_history_df.loc[current_day_index, "volume"]
        change_day_volume = symbol_history_df.loc[change_day_index, "volume"]
        ratio = change_day_volume / current_day_volume

        if ratio >= volume_change_ratio:
            current_day_date = current_row_data["date"]
            change_day_date = symbol_history_df.loc[change_day_index, "date"]
            after_change_day_date = symbol_history_df.loc[
                after_change_day_index, "date"
            ]

            current_day_total_volume = list(
                mongodb_conn.collection.find({"date": current_day_date})
            )
            change_day_total_volume = list(
                mongodb_conn.collection.find({"date": change_day_date})
            )
            after_change_day_total_volume = list(
                mongodb_conn.collection.find({"date": after_change_day_date})
            )

            if (
                current_day_total_volume
                and current_day_total_volume[0]["total_volume"] != 0
            ):
                if change_day_total_volume and 0.9 * volume_change_ratio < (
                    change_day_total_volume[0]["total_volume"]
                    / current_day_total_volume[0]["total_volume"]
                ):
                    VALID_CHANGE_FLAG = False

                if after_change_day_total_volume and 0.9 * volume_change_ratio < (
                    after_change_day_total_volume[0]["total_volume"]
                    / current_day_total_volume[0]["total_volume"]
                ):
                    VALID_CHANGE_FLAG = False

            for forbidden_range in prevent_repeated_strategy_list:
                start, end = forbidden_range
                if current_day_index in range(start, end):
                    VALID_CHANGE_FLAG = False
                    break

            if VALID_CHANGE_FLAG:
                if symbol_history_df.loc[change_day_index, "value"] < 10_000_000:
                    continue

                on_change_comulative_return_amount_list = []
                on_change_comulative_return_percent_list = []
                after_change_comulative_return_amount_list = []
                after_change_comulative_return_percent_list = []
                last_valid_index = 0
                for floating_index in range(1, return_period + 1):
                    if after_change_day_index + floating_index > df_last_index:
                        break

                    else:
                        ###########################################################
                        on_change_day_ahead_return = symbol_history_df.loc[
                            change_day_index + floating_index, "price_change"
                        ]

                        if on_change_comulative_return_amount_list:
                            on_change_day_ahead_return = (
                                on_change_day_ahead_return
                                + on_change_comulative_return_amount_list[-1]
                            )
                        on_change_comulative_return_amount_list.append(
                            on_change_day_ahead_return
                        )

                        on_change_day_ahead_return_percent = (
                            on_change_comulative_return_amount_list[-1]
                            / symbol_history_df.loc[change_day_index, "close_price"]
                        ) * 100
                        on_change_comulative_return_percent_list.append(
                            on_change_day_ahead_return_percent
                        )
                        ###########################################################
                        after_change_day_ahead_return = symbol_history_df.loc[
                            after_change_day_index + floating_index, "price_change"
                        ]

                        if after_change_comulative_return_amount_list:
                            after_change_day_ahead_return = (
                                after_change_day_ahead_return
                                + after_change_comulative_return_amount_list[-1]
                            )
                        after_change_comulative_return_amount_list.append(
                            after_change_day_ahead_return
                        )

                        after_change_day_ahead_return_percent = (
                            after_change_comulative_return_amount_list[-1]
                            / symbol_history_df.loc[
                                after_change_day_index, "close_price"
                            ]
                        ) * 100
                        after_change_comulative_return_percent_list.append(
                            after_change_day_ahead_return_percent
                        )
                        ###########################################################

                    last_valid_index = floating_index

                if (
                    after_change_comulative_return_amount_list
                    and after_change_comulative_return_percent_list
                    and on_change_comulative_return_amount_list
                    and on_change_comulative_return_percent_list
                ):
                    if max(on_change_comulative_return_percent_list) > threshold:
                        on_change_matched_threshold_count += 1

                    if max(after_change_comulative_return_percent_list) > threshold:
                        after_change_matched_threshold_count += 1

                    on_change_period_return = on_change_comulative_return_amount_list[
                        -1
                    ]
                    after_change_period_return = (
                        after_change_comulative_return_amount_list[-1]
                    )

                    on_change_period_return_percent = (
                        on_change_comulative_return_percent_list[-1]
                    )
                    after_change_period_return_percent = (
                        after_change_comulative_return_percent_list[-1]
                    )

                    symbol = current_row_data["symbol"]
                    current_day_date = current_row_data["date"]
                    change_day_date = symbol_history_df.loc[change_day_index, "date"]

                    on_change_return_period_day_date = symbol_history_df.loc[
                        change_day_index + floating_index - 1, "date"
                    ]
                    after_change_return_period_day_date = symbol_history_df.loc[
                        after_change_day_index + floating_index - 1, "date"
                    ]

                    on_change_return_period_day_price = symbol_history_df.loc[
                        change_day_index + floating_index - 1, "close_price"
                    ]
                    after_change_return_period_day_price = symbol_history_df.loc[
                        after_change_day_index + floating_index - 1, "close_price"
                    ]

                    new_matched_strategy = {
                        "inst_id": current_row_data["inst_id"],
                        "asset_name": current_row_data["asset_name"],
                        "symbol": symbol,
                        "current_day_date": current_day_date,
                        "current_day_volume": current_day_volume,
                        "current_day_price": current_row_data["close_price"],
                        "on_change_day_date": change_day_date,
                        "on_change_day_volume": change_day_volume,
                        "on_change_day_price": symbol_history_df.loc[
                            change_day_index, "close_price"
                        ],
                        "after_change_day_date": symbol_history_df.loc[
                            after_change_day_index, "date"
                        ],
                        "after_change_day_volume": symbol_history_df.loc[
                            after_change_day_index, "volume"
                        ],
                        "after_change_day_price": symbol_history_df.loc[
                            after_change_day_index, "close_price"
                        ],
                        "on_change_return_period_day_date": on_change_return_period_day_date,
                        "on_change_return_period_day_price": on_change_return_period_day_price,
                        "on_change_period_return": on_change_period_return,
                        "on_change_period_return_percent": on_change_period_return_percent,
                        "after_change_return_period_day_date": after_change_return_period_day_date,
                        "after_change_return_period_day_price": after_change_return_period_day_price,
                        "after_change_period_return": after_change_period_return,
                        "after_change_period_return_percent": after_change_period_return_percent,
                        "on_change_comulative_return_amount_list": on_change_comulative_return_amount_list,
                        "on_change_comulative_return_percent_list": on_change_comulative_return_percent_list,
                        "after_change_comulative_return_amount_list": after_change_comulative_return_amount_list,
                        "after_change_comulative_return_percent_list": after_change_comulative_return_percent_list,
                    }
                    matched_strategy_list.append(new_matched_strategy)

                    start_index = change_day_index
                    end_index = change_day_index + last_valid_index
                    prevent_repeated_strategy_list.append((start_index, end_index))

    if matched_strategy_list:
        matched_strategy_list_df = pd.DataFrame(matched_strategy_list)

        #######################################################################
        matched_strategy_list_df["on_change_max_comulative_return_percent"] = (
            matched_strategy_list_df.apply(
                add_on_change_max_comulative_return_percent, axis=1
            )
        )
        matched_strategy_list_df.dropna(inplace=True)

        matched_strategy_list_df["after_change_max_comulative_return_percent"] = (
            matched_strategy_list_df.apply(
                add_after_change_max_comulative_return_percent, axis=1
            )
        )
        matched_strategy_list_df.dropna(inplace=True)
        #######################################################################
        matched_strategy_list_df["on_change_day_of_max_percent"] = (
            matched_strategy_list_df.apply(add_on_change_day_of_max_percent, axis=1)
        )
        matched_strategy_list_df.dropna(inplace=True)

        matched_strategy_list_df["after_change_day_of_max_percent"] = (
            matched_strategy_list_df.apply(add_after_change_day_of_max_percent, axis=1)
        )
        matched_strategy_list_df.dropna(inplace=True)
        #######################################################################

        matched_strategy_list_df["on_change_day_of_pass_threshold"] = (
            matched_strategy_list_df.apply(
                add_on_change_day_of_pass_threshold, axis=1, threshold=threshold
            )
        )
        matched_strategy_list_df.dropna(inplace=True)

        matched_strategy_list_df["after_change_day_of_pass_threshold"] = (
            matched_strategy_list_df.apply(
                add_after_change_day_of_pass_threshold, axis=1, threshold=threshold
            )
        )
        matched_strategy_list_df.dropna(inplace=True)
        #######################################################################
        on_change_mean_of_max_comulative_return_percent = matched_strategy_list_df[
            "on_change_max_comulative_return_percent"
        ].mean()
        on_change_mean_of_max_comulative_return_percent_list.append(
            on_change_mean_of_max_comulative_return_percent
        )

        after_change_mean_of_max_comulative_return_percent = matched_strategy_list_df[
            "after_change_max_comulative_return_percent"
        ].mean()
        after_change_mean_of_max_comulative_return_percent_list.append(
            after_change_mean_of_max_comulative_return_percent
        )
        #######################################################################
        on_change_day_of_max_percent_mean = matched_strategy_list_df[
            "on_change_day_of_max_percent"
        ].mean()
        on_change_day_to_max_return_percent_list.append(
            on_change_day_of_max_percent_mean
        )

        after_change_day_of_max_percent_mean = matched_strategy_list_df[
            "after_change_day_of_max_percent"
        ].mean()
        after_change_day_to_max_return_percent_list.append(
            after_change_day_of_max_percent_mean
        )

        matched_strategy_list = matched_strategy_list_df.to_dict(orient="records")

    return (
        matched_strategy_list,
        on_change_matched_threshold_count,
        on_change_mean_of_max_comulative_return_percent_list,
        on_change_day_to_max_return_percent_list,
        after_change_matched_threshold_count,
        after_change_mean_of_max_comulative_return_percent_list,
        after_change_day_to_max_return_percent_list,
    )
