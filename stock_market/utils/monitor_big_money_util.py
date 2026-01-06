import pandas as pd
import numpy as np

from core.utils import MongodbInterface
from core.configs import (
    STOCK_MONGO_DB,
    RIAL_TO_BILLION_TOMAN,
    BIG_MONEY_ALERTS_COLLECTION,
    BIG_MONEY_THRESHOLD_BILLION,
)
from stock_market.utils import STOCK_PAPER, get_market_watch_data_from_mongo


def save_snapshot(mongo_interface: MongodbInterface, df):
    """Saves raw values for the next comparison cycle without manual renaming."""
    snapshot = df.to_dict(orient="records")

    mongo_interface.insert_docs_into_collection(snapshot)


def add_buy_sell_value(market_watch_df):
    market_watch_df = market_watch_df[market_watch_df["paper_type"] == STOCK_PAPER]
    market_watch_df = market_watch_df[
        [
            "ins_code",
            "symbol",
            "name",
            "last_date",
            "last_time",
            "closing_price",
            "individual_buy_volume",
            "individual_sell_volume",
            "individual_buy_count",
            "individual_sell_count",
        ]
    ]

    market_watch_df[["individual_buy_value", "individual_sell_value"]] = (
        market_watch_df[["individual_buy_volume", "individual_sell_volume"]].mul(
            market_watch_df["closing_price"], axis=0
        )
    )

    return market_watch_df


def monitor_big_money(current_df):
    current_df = add_buy_sell_value(current_df)

    prev_df = get_market_watch_data_from_mongo()
    prev_df = add_buy_sell_value(prev_df)

    merged = pd.merge(
        current_df, prev_df, on="ins_code", how="left", suffixes=("", "_prev")
    ).fillna(0)

    merged["value_diff"] = (
        merged["individual_buy_value"] - merged["individual_buy_value_prev"]
    ) / RIAL_TO_BILLION_TOMAN
    merged["count_diff"] = (
        merged["individual_buy_count"] - merged["individual_buy_count_prev"]
    )
    merged["value_mean"] = (merged["value_diff"] / merged["count_diff"]).fillna(0)
    buy_alerts = merged[(merged["value_mean"]) >= BIG_MONEY_THRESHOLD_BILLION].copy(
        deep=True
    )
    buy_alerts["side"] = "buy"

    merged["value_diff"] = (
        merged["individual_sell_value"] - merged["individual_sell_value_prev"]
    ) / RIAL_TO_BILLION_TOMAN
    merged["count_diff"] = (
        merged["individual_sell_count"] - merged["individual_sell_count_prev"]
    )
    merged["value_mean"] = (merged["value_diff"] / merged["count_diff"]).fillna(0)
    sell_alerts = merged[(merged["value_mean"]) >= BIG_MONEY_THRESHOLD_BILLION].copy(
        deep=True
    )
    sell_alerts["side"] = "sell"

    new_alerts = pd.concat([buy_alerts, sell_alerts], ignore_index=True)
    new_alerts = new_alerts[
        ["symbol", "name", "last_date", "last_time", "value_mean", "count_diff", "side"]
    ]
    new_alerts.replace([np.inf, -np.inf], np.nan, inplace=True)
    new_alerts.dropna(inplace=True)
    new_alerts = new_alerts.to_dict(orient="records")

    if new_alerts:
        mongo_alerts = MongodbInterface(
            db_name=STOCK_MONGO_DB, collection_name=BIG_MONEY_ALERTS_COLLECTION
        )
        prev_alerts = pd.DataFrame(
            list(mongo_alerts.collection.find({}, {"_id": 0}))
        ).to_dict(orient="records")

        all_alerts = (prev_alerts + new_alerts)[0:300]

        mongo_alerts.insert_docs_into_collection(all_alerts)
