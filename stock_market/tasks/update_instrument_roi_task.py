import pandas as pd

from core.configs import (
    STOCK_MONGO_DB,
    RIAL_TO_BILLION_TOMAN,
    STOCK_NA_ROI,
    AUTO_MODE,
    MANUAL_MODE,
)
from core.utils import MongodbInterface, run_main_task
from stock_market.utils import (
    MAIN_PAPER_TYPE_DICT,
    FUND_PAPER,
    get_market_watch_data_from_redis,
    is_market_open,
)


def add_link(row):
    ins_code = row.get("ins_code")
    link = f"https://www.tsetmc.com/instInfo/{ins_code}"

    return link


def add_pe(row):
    row = row.to_dict()
    close_mean = row.get("close_mean")
    eps = row.get("eps")
    try:
        pe = close_mean / eps
    except Exception:
        pe = 0

    return pe


def add_ps(row):
    row = row.to_dict()
    close_mean = row.get("close_mean")
    psr = row.get("psr")
    try:
        ps = close_mean / psr
    except Exception:
        ps = 0

    return ps


def add_market_cap(row):
    row = row.to_dict()

    paper_type = row.get("paper_id")
    if paper_type == FUND_PAPER:
        market_cap = 0
        return market_cap

    close_mean = row.get("close_mean")
    total_share = row.get("total_share")
    try:
        market_cap = (close_mean * total_share) / RIAL_TO_BILLION_TOMAN
    except Exception:
        market_cap = 0

    return market_cap


def update_instrument_duration_roi(instrument_info: pd.DataFrame):

    instrument_info["link"] = instrument_info.apply(add_link, axis=1)
    instrument_info["pe"] = instrument_info.apply(add_pe, axis=1)
    instrument_info["ps"] = instrument_info.apply(add_ps, axis=1)
    instrument_info["market_cap"] = instrument_info.apply(add_market_cap, axis=1)

    instrument_info = instrument_info[
        instrument_info["paper_id"].isin(list(MAIN_PAPER_TYPE_DICT.keys()))
    ]
    instrument_info = instrument_info[
        [
            "ins_code",
            "symbol",
            "link",
            "industrial_group_id",
            "industrial_group_name",
            "market_id",
            "market_name",
            "paper_id",
            "paper_name",
            "pe",
            "ps",
            "sector_pe",
            "market_cap",
            "daily_roi",
            "weekly_roi",
            "monthly_roi",
            "quarterly_roi",
            "half_yearly_roi",
            "yearly_roi",
            "three_years_roi",
        ]
    ]
    instrument_info = instrument_info.to_dict(orient="records")

    if instrument_info:
        mongo_conn = MongodbInterface(db_name=STOCK_MONGO_DB, collection_name="roi")
        mongo_conn.insert_docs_into_collection(documents=instrument_info)
        mongo_conn.client.close()


def calculate_industry_duration_roi(durations: dict):
    mongo_conn = MongodbInterface(db_name=STOCK_MONGO_DB, collection_name="roi")
    roi = list(mongo_conn.collection.find({}, {"_id": 0}))
    roi = pd.DataFrame(roi)
    mongo_conn.client.close()

    industry_roi_list = list()
    unique_industry_id_list = roi["industrial_group_id"].unique().tolist()
    for industry_id in unique_industry_id_list:
        industry_roi = roi[roi["industrial_group_id"] == industry_id]
        if industry_roi.empty:
            continue

        new_roi = {
            "industrial_group_id": industry_id,
            "industrial_group_name": industry_roi.iloc[0].get("industrial_group_name"),
        }
        for _, duration_name in durations.items():
            industry_roi = industry_roi[industry_roi[duration_name] != STOCK_NA_ROI]
            if industry_roi.empty:
                new_roi[duration_name] = STOCK_NA_ROI
            else:
                new_roi[duration_name] = industry_roi[duration_name].mean()

        industry_roi_list.append(new_roi)

    if industry_roi_list:
        mongo_conn = MongodbInterface(
            db_name=STOCK_MONGO_DB, collection_name="industry_ROI"
        )
        mongo_conn.insert_docs_into_collection(documents=industry_roi_list)
        mongo_conn.client.close()


def update_instrument_roi_main(run_mode):
    if run_mode == MANUAL_MODE or is_market_open():
        mongo_conn = MongodbInterface(
            db_name=STOCK_MONGO_DB, collection_name="instrument_info"
        )
        instrument_info = pd.DataFrame(mongo_conn.collection.find({}, {"_id": 0}))
        mongo_conn.client.close()

        last_data = get_market_watch_data_from_redis()
        if last_data.empty:
            return

        last_data["daily_roi"] = (
            last_data["last_price_change"] / last_data["yesterday_price"]
        ) * 100
        last_data["close_mean"] = last_data["closing_price"]
        last_data = last_data[["ins_code", "daily_roi", "close_mean"]]

        instrument_info = pd.merge(left=instrument_info, right=last_data, on="ins_code")

        durations = {
            7: "weekly_roi",
            30: "monthly_roi",
            90: "quarterly_roi",
            180: "half_yearly_roi",
            365: "yearly_roi",
            1095: "three_years_roi",
        }

        update_instrument_duration_roi(instrument_info=instrument_info)

        calculate_industry_duration_roi(durations=durations)


def update_instrument_roi(run_mode: str = AUTO_MODE):

    run_main_task(
        main_task=update_instrument_roi_main,
        kw_args={"run_mode": run_mode},
    )
