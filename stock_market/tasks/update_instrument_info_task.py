from datetime import datetime, timedelta
import pandas as pd
from tqdm import tqdm

from core.configs import STOCK_MONGO_DB, STOCK_NA_ROI
from core.utils import (
    MongodbInterface,
    TSETMC_REQUEST_HEADERS,
    get_http_response,
    replace_arabic_letters,
    get_deviation_percent,
    run_main_task,
)

from stock_market.utils import MAIN_MARKET_TYPE_DICT, ALL_PAPER_TYPE_DICT
from stock_market.models import StockInstrument


def get_historical_roi(ins_code):
    durations = {
        7: "weekly_roi",
        30: "monthly_roi",
        90: "quarterly_roi",
        180: "half_yearly_roi",
        365: "yearly_roi",
        1095: "three_years_roi",
    }

    historical_roi = {
        "weekly_roi": STOCK_NA_ROI,
        "monthly_roi": STOCK_NA_ROI,
        "quarterly_roi": STOCK_NA_ROI,
        "half_yearly_roi": STOCK_NA_ROI,
        "yearly_roi": STOCK_NA_ROI,
        "three_years_roi": STOCK_NA_ROI,
    }

    mongo_conn = MongodbInterface(
        db_name=STOCK_MONGO_DB, collection_name="adjusted_history"
    )
    query_filter = {"ins_code": f"{ins_code}"}
    full_history = mongo_conn.collection.find_one(query_filter, {"_id": 0})

    if full_history is None:

        return historical_roi

    full_history = pd.DataFrame(full_history.get("adjusted_history", []))
    if full_history.empty:

        return historical_roi

    range_end_price = full_history.iloc[-1]
    range_end_price = (range_end_price.to_dict()).get("close_mean")

    for duration_int, duration_name in durations.items():
        today = datetime.today().timestamp()
        range_start = today - timedelta(days=duration_int).total_seconds()

        filtered_history = full_history[full_history["trade_date"] >= range_start]
        if filtered_history.empty:
            continue

        range_start_price = filtered_history.iloc[0]
        range_start_price = (range_start_price.to_dict()).get("close_mean")
        roi = get_deviation_percent(range_end_price, range_start_price)
        historical_roi[duration_name] = roi

    return historical_roi


def update_instrument_info_main():
    mongo_conn = MongodbInterface(
        db_name=STOCK_MONGO_DB, collection_name="instrument_info"
    )

    all_instruments = StockInstrument.objects.all()
    for ins_obj in tqdm(all_instruments, desc="Instrument info", ncols=10):
        market_id = ins_obj.market_type
        paper_id = ins_obj.paper_type
        URL = f"https://cdn.tsetmc.com/api/Instrument/GetInstrumentInfo/{ins_obj.ins_code}"

        instrument_info = get_http_response(
            req_url=URL, req_headers=TSETMC_REQUEST_HEADERS
        )
        instrument_info = instrument_info.json()
        instrument_info = instrument_info.get("instrumentInfo")

        info = {
            "ins_code": ins_obj.ins_code,
            "symbol": replace_arabic_letters(instrument_info.get("lVal18AFC")),
            "name": replace_arabic_letters(instrument_info.get("lVal30")),
            "last_update": instrument_info.get("dEven"),
            "industrial_group_id": ins_obj.industrial_group.id,
            "industrial_group_name": replace_arabic_letters(
                ins_obj.industrial_group.name
            ),
            "market_id": market_id,
            "market_name": MAIN_MARKET_TYPE_DICT.get(market_id),
            "sub_market": instrument_info.get("cgrValCotTitle"),
            "paper_id": paper_id,
            "paper_name": ALL_PAPER_TYPE_DICT.get(paper_id),
            "total_share": instrument_info.get("zTitad"),
            "month_mean_volume": instrument_info.get("qTotTran5JAvg"),
            "base_volume": instrument_info.get("baseVol"),
            "sector_pe": instrument_info.get("eps").get("sectorPE"),
            "psr": instrument_info.get("eps").get("psr"),
        }

        try:
            eps = instrument_info.get("eps").get("estimatedEPS")
            info["eps"] = float(eps)
        except Exception:
            info["eps"] = 0

        try:
            floating_volume = instrument_info.get("kAjCapValCpsIdx")
            info["floating_volume"] = float(floating_volume)
        except Exception:
            info["floating_volume"] = 0

        historical_roi = get_historical_roi(ins_obj.ins_code)
        info.update(historical_roi)
        query = {"ins_code": ins_obj.ins_code}
        mongo_conn.collection.delete_many(filter=query)
        mongo_conn.collection.insert_one(info)


def update_instrument_info():

    run_main_task(
        main_task=update_instrument_info_main,
        daily=True,
    )
