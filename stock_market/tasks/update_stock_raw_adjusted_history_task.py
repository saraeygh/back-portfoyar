from datetime import datetime
from tqdm import tqdm
import pandas as pd

from core.utils import get_http_response, run_main_task

from stock_market.utils import (
    TSETMC_REQUEST_HEADERS,
    HISTORY_COLUMN_RENAME,
    update_get_existing_industrial_group,
    update_get_existing_instrument,
    update_stock_raw_history,
    update_stock_adjusted_history,
)


def convert_date_str_to_obj(row):
    date_str = str(row.get("trade_date"))
    date_obj = datetime.strptime(date_str, "%Y%m%d").date()

    return date_obj


def update_stock_raw_adjusted_history_main():

    existing_industrial_group = update_get_existing_industrial_group()
    existing_instrument = update_get_existing_instrument(existing_industrial_group)
    del existing_industrial_group

    for ins_code, instrument_obj in tqdm(
        existing_instrument.items(), desc="Stock history", ncols=10
    ):
        PRICE_HISTORY_URL = f"https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/{ins_code}/0"
        CLIENT_TYPE_HISTORY_URL = (
            f"https://cdn.tsetmc.com/api/ClientType/GetClientTypeHistory/{ins_code}"
        )

        price_history = get_http_response(
            req_url=PRICE_HISTORY_URL, req_headers=TSETMC_REQUEST_HEADERS
        )
        try:
            price_history = price_history.json()
            price_history = price_history.get("closingPriceDaily")
            price_history = pd.DataFrame(price_history)
            price_history.rename(
                columns={"dEven": "date", "insCode": "ins_code"}, inplace=True
            )
        except Exception:
            continue

        client_type = get_http_response(
            req_url=CLIENT_TYPE_HISTORY_URL, req_headers=TSETMC_REQUEST_HEADERS
        )
        try:
            client_type = client_type.json()
            client_type = client_type.get("clientType")
            client_type = pd.DataFrame(client_type)
            client_type.rename(columns={"recDate": "date"}, inplace=True)
        except Exception:
            continue

        if not price_history.empty and not client_type.empty:
            history = pd.merge(
                left=price_history, right=client_type, how="left", on="date"
            )
            del price_history
            del client_type
            history = history.fillna(0)

            history.rename(columns=HISTORY_COLUMN_RENAME, inplace=True)

            history["trade_date"] = history.apply(convert_date_str_to_obj, axis=1)

            history = history.drop_duplicates(subset="trade_date")

            history.sort_values(by="trade_date", ascending=True, inplace=True)

            update_stock_raw_history(raw_history=history, instrument_obj=instrument_obj)

    update_stock_adjusted_history()


def update_stock_raw_adjusted_history():

    run_main_task(
        main_task=update_stock_raw_adjusted_history_main,
        daily=True,
    )
