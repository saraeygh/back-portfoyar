from datetime import datetime
from tqdm import tqdm
import pandas as pd
from colorama import Fore, Style

from core.utils import TSETMC_REQUEST_HEADERS, get_http_response, run_main_task

from stock_market.utils import (
    HISTORY_COLUMN_RENAME,
    update_get_existing_industrial_group,
    update_get_existing_instrument,
    update_stock_raw_history,
    remove_expired_instruments,
)


def convert_date_str_to_obj(row):
    date_str = str(row.get("trade_date"))
    date_obj = datetime.strptime(date_str, "%Y%m%d").date()

    return date_obj


def update_stock_full_raw_history_main():
    print(Fore.BLUE + "update_get_existing_industrial_group" + Style.RESET_ALL)
    update_get_existing_industrial_group()
    print(Fore.BLUE + "update_get_existing_instrument" + Style.RESET_ALL)
    update_get_existing_instrument()

    all_instruments = remove_expired_instruments()
    for instrument_obj in tqdm(all_instruments, desc="Stock history", ncols=10):
        PRICE_HISTORY_URL = f"https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/{instrument_obj.ins_code}/0"
        price_history = get_http_response(
            req_url=PRICE_HISTORY_URL, req_headers=TSETMC_REQUEST_HEADERS
        )
        price_history = price_history.json()
        price_history = price_history.get("closingPriceDaily", [])
        price_history = pd.DataFrame(price_history)
        if price_history.empty:
            continue
        price_history.rename(
            columns={"dEven": "date", "insCode": "ins_code"}, inplace=True
        )

        CLIENT_TYPE_HISTORY_URL = f"https://cdn.tsetmc.com/api/ClientType/GetClientTypeHistory/{instrument_obj.ins_code}"
        client_type = get_http_response(
            req_url=CLIENT_TYPE_HISTORY_URL, req_headers=TSETMC_REQUEST_HEADERS
        )
        client_type = client_type.json()
        client_type = client_type.get("clientType", [])
        client_type = pd.DataFrame(client_type)
        if client_type.empty:
            continue
        client_type.rename(columns={"recDate": "date"}, inplace=True)

        if not price_history.empty and not client_type.empty:
            history = pd.merge(
                left=price_history, right=client_type, how="left", on="date"
            )
            history = history.fillna(0)
            history.rename(columns=HISTORY_COLUMN_RENAME, inplace=True)
            history["trade_date"] = history.apply(convert_date_str_to_obj, axis=1)
            history = history.drop_duplicates(subset="trade_date")
            history.sort_values(by="trade_date", ascending=True, inplace=True)

            update_stock_raw_history(raw_history=history, instrument_obj=instrument_obj)


def update_stock_full_raw_history():

    run_main_task(
        main_task=update_stock_full_raw_history_main,
        daily=True,
    )
