from datetime import datetime, timedelta
import pandas as pd
from core.configs import STOCK_MONGO_DB, STOCK_NA_ROI
from core.utils import (
    MongodbInterface,
    get_http_response,
    task_timing,
    replace_arabic_letters,
    get_deviation_percent,
)
from stock_market.utils import (
    TSETMC_REQUEST_HEADERS,
    MAIN_MARKET_TYPE_DICT,
    ALL_PAPER_TYPE_DICT,
)
from stock_market.utils import (
    update_get_existing_industrial_group,
    update_get_existing_instrument,
)
from tqdm import tqdm


mongo_client = MongodbInterface(
    db_name=STOCK_MONGO_DB, collection_name="adjusted_history"
)


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

    query_filter = {"ins_code": f"{ins_code}"}
    full_history = mongo_client.collection.find_one(query_filter, {"_id": 0})
    if full_history is None:
        return historical_roi
    full_history = pd.DataFrame(full_history["adjusted_history"])
    if full_history.empty:
        return historical_roi

    full_history.sort_values(by="trade_date", inplace=True, ascending=False)
    full_history.reset_index(drop=True, inplace=True)
    range_end_price = full_history.iloc[0]
    range_end_price = (range_end_price.to_dict()).get("close_mean")

    for duration_int, duration_name in durations.items():
        try:
            today = datetime.today()
            today_timestamp = today.timestamp()
            range_start = today - timedelta(days=duration_int)
            range_start = range_start.timestamp()

            filtered_history = full_history[full_history["trade_date"] <= range_start]
            if filtered_history.empty:
                continue

            filtered_history.sort_values(by="trade_date", inplace=True, ascending=False)
            filtered_history.reset_index(drop=True, inplace=True)
            range_start_price = filtered_history.iloc[0]
            range_start_price_date = range_start_price.get("trade_date")

            if range_start * 0.9 < range_start_price_date < today_timestamp:
                range_start_price = (range_start_price.to_dict()).get("close_mean")
                roi = get_deviation_percent(range_end_price, range_start_price)
                if abs(roi) < 3000:
                    historical_roi[duration_name] = roi

        except Exception:
            continue

    return historical_roi


@task_timing
def update_instrument_info():
    existing_industrial_group = update_get_existing_industrial_group()
    existing_instruments = update_get_existing_instrument(existing_industrial_group)

    documents = list()
    for ins_code, ins_obj in tqdm(
        existing_instruments.items(), desc="Instrument info", ncols=10
    ):
        market_id = ins_obj.market_type
        paper_id = ins_obj.paper_type
        URL = f"https://cdn.tsetmc.com/api/Instrument/GetInstrumentInfo/{ins_code}"

        instrument_info = get_http_response(
            req_url=URL, req_headers=TSETMC_REQUEST_HEADERS
        )
        try:
            instrument_info = instrument_info.json()
            instrument_info = instrument_info.get("instrumentInfo")

            info = {
                "ins_code": ins_code,
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

            eps = instrument_info.get("eps").get("estimatedEPS")
            try:
                info["eps"] = float(eps)
            except Exception:
                info["eps"] = 0

            floating_volume = instrument_info.get("kAjCapValCpsIdx")
            try:
                info["floating_volume"] = float(floating_volume)
            except Exception:
                info["floating_volume"] = 0

        except Exception:
            continue

        historical_roi = get_historical_roi(ins_code)
        info.update(historical_roi)
        documents.append(info)

    mongo_client.collection = mongo_client.db["instrument_info"]
    mongo_client.insert_docs_into_collection(documents=documents)
