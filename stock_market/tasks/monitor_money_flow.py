import pandas as pd
import jdatetime as jdt
from celery import shared_task
from datetime import datetime
import pytz

from core.utils import MongodbInterface, run_main_task, is_market_open_today
from core.configs import (
    STOCK_MONGO_DB,
    RIAL_TO_BILLION_TOMAN,
    AUTO_MODE,
    TEHRAN_TZ,
)
from stock_market.utils import (
    get_market_watch_data_from_mongo,
    is_in_schedule,
)

# Collections
SNAPSHOT_COLLECTION = "individual_trade_snapshot"
ALERTS_COLLECTION = "huge_money_influx_alerts"
THRESHOLD_BILLION = 5


def monitor_money_influx_main(run_mode=AUTO_MODE):
    #  Market Schedule Check
    if (
        not (is_in_schedule(9, 0, 0, 12, 30, 0) and is_market_open_today())
        and run_mode == AUTO_MODE
    ):
        return

    #  Get Current Data
    current_df = get_market_watch_data_from_mongo()
    if current_df.empty:
        return

    # Calculate current cumulative values for individuals
    # Uses 'closing_price' (pcl) as requested
    current_df["buy_val_ind"] = current_df["closing_price"] * current_df["buy_volumeI"]
    current_df["sell_val_ind"] = (
        current_df["closing_price"] * current_df["sell_volumeI"]
    )

    #  Get Last Snapshot
    mongo_snap = MongodbInterface(
        db_name=STOCK_MONGO_DB, collection_name=SNAPSHOT_COLLECTION
    )
    prev_data = list(mongo_snap.collection.find({}, {"_id": 0}))

    if not prev_data:
        # First run: save current state and exit
        save_snapshot(mongo_snap, current_df)
        return

    prev_df = pd.DataFrame(prev_data)

    #  Merge and Compare
    # We use suffixes to distinguish current from previous values automatically
    merged = pd.merge(
        current_df[
            [
                "ins_code",
                "symbol",
                "buy_val_ind",
                "sell_val_ind",
                "buy_countI",
                "sell_countI",
            ]
        ],
        prev_df[
            ["ins_code", "buy_val_ind", "sell_val_ind", "buy_countI", "sell_countI"]
        ],
        on="ins_code",
        how="left",
        suffixes=("", "_prev"),  # Adds _prev to the old data
    ).fillna(0)

    #  Calculate Differences (Current - 5 Minutes Ago)
    merged["buy_value_diff_btn"] = (
        merged["buy_val_ind"] - merged["buy_val_ind_prev"]
    ) / RIAL_TO_BILLION_TOMAN
    merged["sell_value_diff_btn"] = (
        merged["sell_val_ind"] - merged["sell_val_ind_prev"]
    ) / RIAL_TO_BILLION_TOMAN

    # Difference in count of people (individuals)
    merged["buy_count_diff"] = merged["buy_countI"] - merged["buy_countI_prev"]
    merged["sell_count_diff"] = merged["sell_countI"] - merged["sell_countI_prev"]

    #  Detect Huge Influxes (> 5 Billion Toman)
    buy_alerts = merged[merged["buy_value_diff_btn"] >= THRESHOLD_BILLION]
    sell_alerts = merged[merged["sell_value_diff_btn"] >= THRESHOLD_BILLION]

    all_alerts = []
    tehran_now = datetime.now(pytz.timezone(TEHRAN_TZ))
    shamsi_date = str(jdt.date.today().strftime("%Y/%m/%d"))

    # Format Buy Alerts
    for _, row in buy_alerts.iterrows():
        all_alerts.append(
            {
                "ins_code": row["ins_code"],
                "symbol": row["symbol"],
                "side": "BUY",
                "influx_value_billion": round(row["buy_value_diff_btn"], 2),
                "individual_count_diff": int(row["buy_count_diff"]),
                "time": tehran_now.strftime("%H:%M:%S"),
                "date": shamsi_date,
                "type": "RETAIL_MONEY_INFLUX",
            }
        )

    # Format Sell Alerts
    for _, row in sell_alerts.iterrows():
        all_alerts.append(
            {
                "ins_code": row["ins_code"],
                "symbol": row["symbol"],
                "side": "SELL",
                "influx_value_billion": round(row["sell_value_diff_btn"], 2),
                "individual_count_diff": int(row["sell_count_diff"]),
                "time": tehran_now.strftime("%H:%M:%S"),
                "date": shamsi_date,
                "type": "RETAIL_MONEY_IN",
            }
        )

    #  Save Alerts and Update Snapshot
    if all_alerts:
        mongo_alerts = MongodbInterface(
            db_name=STOCK_MONGO_DB, collection_name=ALERTS_COLLECTION
        )
        mongo_alerts.insert_docs_into_collection(all_alerts)

    # Update the snapshot for the next 5-minute cycle
    save_snapshot(mongo_snap, current_df)


def save_snapshot(mongo_interface, df):
    """Saves raw values for the next comparison cycle without manual renaming."""
    snapshot = df[
        ["ins_code", "buy_val_ind", "sell_val_ind", "buy_countI", "sell_countI"]
    ].to_dict(orient="records")

    for doc in snapshot:
        mongo_interface.collection.update_one(
            {"ins_code": doc["ins_code"]}, {"$set": doc}, upsert=True
        )


@shared_task(name="monitor_individual_influx_task")
def monitor_individual_influx(run_mode=AUTO_MODE):
    run_main_task(
        main_task=monitor_individual_influx_main, kw_args={"run_mode": run_mode}
    )
