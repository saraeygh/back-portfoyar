import pandas as pd
import jdatetime
from tqdm import tqdm
from colorama import Fore, Style

from core.configs import OPTION_MONGO_DB, OPTION_REDIS_DB
from core.utils import (
    MongodbInterface,
    RedisInterface,
    get_http_response,
    run_main_task,
)
from stock_market.utils import TSETMC_REQUEST_HEADERS


UNNECESSARY_COLUMNS = [
    "last",
    "id",
    "hEven",
    "iClose",
    "yClose",
]

COLUMNS_NAME_MAPPING = {
    "priceChange": "price_change",
    "priceMin": "price_min",
    "priceMax": "price_max",
    "priceYesterday": "yesterday_price",
    "priceFirst": "first_price",
    "insCode": "inst_id",
    "dEven": "date",
    "pClosing": "close_price",
    "pDrCotVal": "last_trade",
    "zTotTran": "quantity",
    "qTotTran5J": "volume",
    "qTotCap": "value",
}


def convert_date(row, col_name: str = "date"):
    date_str = str(row.get(col_name))
    year, month, day = date_str[0:4], date_str[4:6], date_str[6:]

    shamsi_date = str(
        jdatetime.date.fromgregorian(
            year=int(year),
            month=int(month),
            day=int(day),
        )
    )

    return shamsi_date


def get_update_history(instrument, instrument_type):
    history_data_link = (
        "https://cdn.tsetmc.com/api/ClosingPrice/"
        "GetClosingPriceDailyList/"
        f"{instrument[f"{instrument_type}_ins_code"]}/0"
    )

    option_history_df = get_http_response(
        req_url=history_data_link, req_headers=TSETMC_REQUEST_HEADERS
    )

    try:
        option_history_df = option_history_df.json()
        option_history_df = option_history_df.get("closingPriceDaily")
        option_history_df = pd.DataFrame(option_history_df)

        history_data_link = (
            "https://cdn.tsetmc.com/api/ClosingPrice/"
            "GetClosingPriceDailyList/"
            f"{instrument["base_equity_ins_code"]}/0"
        )
        base_equity_df = get_http_response(
            req_url=history_data_link, req_headers=TSETMC_REQUEST_HEADERS
        )

        base_equity_df = base_equity_df.json()
        base_equity_df = base_equity_df.get("closingPriceDaily")
        base_equity_df = pd.DataFrame(base_equity_df)
        base_equity_df = base_equity_df[["dEven", "pClosing"]]
        base_equity_df = base_equity_df.rename(
            columns={"pClosing": "equit_close_price"}
        )
        option_history_df = pd.merge(
            left=option_history_df, right=base_equity_df, on="dEven", how="left"
        )

        option_history_df = option_history_df.drop(UNNECESSARY_COLUMNS, axis=1)
        option_history_df = option_history_df.rename(columns=COLUMNS_NAME_MAPPING)

        option_history_df["date"] = option_history_df.apply(
            convert_date, axis=1, args=("date",)
        )
        expiration_date = convert_date(row=instrument, col_name="end_date")
        option_history_df["expiration_date"] = expiration_date

        option_history_df["symbol"] = instrument[f"{instrument_type}_symbol"]
        option_history_df["asset_name"] = instrument["base_equity_symbol"]
        option_history_df["strike"] = instrument["strike_price"]

        option_history_df = option_history_df.to_dict(orient="records")

        mongodb_conn = MongodbInterface(
            db_name=OPTION_MONGO_DB, collection_name="history"
        )

        query_filter = {"option_symbol": instrument[f"{instrument_type}_symbol"]}
        mongodb_conn.collection.delete_one(query_filter)

        mongodb_conn.collection.insert_one(
            {
                "option_symbol": instrument[f"{instrument_type}_symbol"],
                "history": option_history_df,
            }
        )

    except Exception as e:
        print(Fore.RED + f"{e}" + Style.RESET_ALL)
        return


def get_option_history_main():
    redis_conn = RedisInterface(db=OPTION_REDIS_DB)
    all_instruments = redis_conn.get_list_of_dicts(list_key="option_data")

    for instrument in tqdm(
        all_instruments, desc=f"Options history, #{len(all_instruments) * 2}", ncols=10
    ):
        get_update_history(instrument=instrument, instrument_type="put")
        get_update_history(instrument=instrument, instrument_type="call")


def get_option_history():

    run_main_task(
        main_task=get_option_history_main,
        daily=True,
    )
