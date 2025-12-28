import pandas as pd

from celery import shared_task

from core.utils import MongodbInterface, run_main_task, is_market_open_today
from core.configs import (
    AUTO_MODE,
    MANUAL_MODE,
    STOCK_MONGO_DB,
    RIAL_TO_BILLION_TOMAN,
    BIG_MONEY_SNAPSHOT_COLLECTION,
    BIG_MONEY_ALERTS_COLLECTION,
    BIG_MONEY_THRESHOLD_BILLION,
)
from stock_market.utils import (
    STOCK_PAPER,
    get_market_watch_data_from_mongo,
    is_in_schedule,
)


def monitor_big_money_main(run_mode):
    if (
        is_in_schedule(9, 0, 0, 18, 00, 0) and is_market_open_today()
    ) or run_mode == MANUAL_MODE:

        current_df = get_market_watch_data_from_mongo()
        current_df = current_df[current_df["paper_type"] == STOCK_PAPER]
        current_df = current_df[
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

        current_df[["individual_buy_value", "individual_sell_value"]] = current_df[
            ["individual_buy_volume", "individual_sell_volume"]
        ].mul(current_df["closing_price"], axis=0)

        mongo_snap = MongodbInterface(
            db_name=STOCK_MONGO_DB, collection_name=BIG_MONEY_SNAPSHOT_COLLECTION
        )
        prev_data = list(mongo_snap.collection.find({}, {"_id": 0}))

        if not prev_data:
            # First run: save current state and exit
            save_snapshot(mongo_snap, current_df)

        prev_df = pd.DataFrame(prev_data)

        #  Merge and Compare
        # We use suffixes to distinguish current from previous values automatically
        merged = pd.merge(
            current_df,
            prev_df,
            on="ins_code",
            how="left",
            suffixes=("", "_prev"),  # Adds _prev to the old data
        ).fillna(0)

        #  Calculate Differences (Current - 5 Minutes Ago)
        merged["buy_value_diff"] = (
            merged["individual_buy_value"] - merged["individual_buy_value_prev"]
        ) / RIAL_TO_BILLION_TOMAN
        merged["sell_value_diff"] = (
            merged["individual_sell_value"] - merged["individual_sell_value_prev"]
        ) / RIAL_TO_BILLION_TOMAN

        # Difference in count of people (individuals)
        merged["buy_count_diff"] = (
            merged["individual_buy_count"] - merged["individual_buy_count_prev"]
        )
        merged["sell_count_diff"] = (
            merged["individual_sell_count"] - merged["individual_sell_count_prev"]
        )

        #  Detect Huge Influxes
        buy_alerts = merged[
            (merged["buy_value_diff"] >= BIG_MONEY_THRESHOLD_BILLION)
            & (merged["buy_count_diff"] >= 1)
            & (merged["buy_count_diff"] <= 5)
        ]
        buy_alerts["side"] = "buy"

        sell_alerts = merged[
            (merged["sell_value_diff"] >= BIG_MONEY_THRESHOLD_BILLION)
            & (merged["sell_count_diff"] >= 1)
            & (merged["sell_count_diff"] <= 5)
        ]
        sell_alerts["side"] = "sell"

        new_alerts = pd.concat([buy_alerts, sell_alerts], ignore_index=True)
        new_alerts = new_alerts[
            [
                "ins_code",
                "symbol",
                "name",
                "last_date",
                "last_time",
                "buy_value_diff",
                "sell_value_diff",
                "buy_count_diff",
                "sell_count_diff",
                "side",
            ]
        ]
        new_alerts = new_alerts.to_dict(orient="records")

        #  Save Alerts and Update Snapshot
        if new_alerts:
            mongo_alerts = MongodbInterface(
                db_name=STOCK_MONGO_DB, collection_name=BIG_MONEY_ALERTS_COLLECTION
            )
            prev_alerts = pd.DataFrame(
                list(mongo_alerts.collection.find({}, {"_id": 0}))
            ).to_dict(orient="records")

            all_alerts = (prev_alerts + new_alerts)[0:300]

            mongo_alerts.insert_docs_into_collection(all_alerts)

        # Update the snapshot for the next 5-minute cycle
        save_snapshot(mongo_snap, current_df)


def save_snapshot(mongo_interface: MongodbInterface, df):
    """Saves raw values for the next comparison cycle without manual renaming."""
    snapshot = df.to_dict(orient="records")

    mongo_interface.insert_docs_into_collection(snapshot)


@shared_task(name="monitor_big_money_task", expires=60)
def monitor_big_money(run_mode=AUTO_MODE):
    run_main_task(main_task=monitor_big_money_main, kw_args={"run_mode": run_mode})
