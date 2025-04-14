import pandas as pd
from colorama import Fore, Style

from core.utils import (
    TSETMC_REQUEST_HEADERS,
    MongodbInterface,
    run_main_task,
    get_http_response,
    replace_arabic_letters_pd,
)
from core.configs import AUTO_MODE, MANUAL_MODE, OPTION_MONGO_DB, OPTION_DATA_COLLECTION

from stock_market.utils import get_last_market_watch_data, is_in_schedule

from option_market.utils import (
    COMMON_OPTION_COLUMN,
    BASE_EQUITY_COLUMNS,
    CALL_OPTION_COLUMN,
    PUT_OPTION_COLUMN,
    TSE_ORDER_BOOK,
    populate_all_option_strategy_async,
    # populate_all_option_strategy_sync,
    convert_int_date_to_str_date,
)


def add_base_equity_best_orders(row, order_index):
    best_order = row.get("base_equity_order_book")
    best_order = best_order[0]

    return best_order[order_index]


def rename_order_book_cols(row):
    order_book = pd.DataFrame(row.get("blDs"))
    order_book.rename(columns=TSE_ORDER_BOOK, inplace=True)
    order_book = order_book[list(TSE_ORDER_BOOK.values())]
    order_book = order_book.to_dict(orient="records")

    return order_book


def update_option_data_from_tse_main(run_mode):
    if run_mode == MANUAL_MODE or is_in_schedule(8, 59, 30, 12, 35, 0):

        URL = "https://cdn.tsetmc.com/api/Instrument/GetInstrumentOptionMarketWatch/0"

        option_data = get_http_response(req_url=URL, req_headers=TSETMC_REQUEST_HEADERS)
        option_data = option_data.json()
        option_data = option_data.get("instrumentOptMarketWatch")
        option_data = pd.DataFrame(option_data)
        option_data = option_data.rename(columns=COMMON_OPTION_COLUMN)
        option_data = option_data.rename(columns=BASE_EQUITY_COLUMNS)
        option_data = option_data.rename(columns=CALL_OPTION_COLUMN)
        option_data = option_data.rename(columns=PUT_OPTION_COLUMN)

        option_data["base_equity_symbol"] = option_data.apply(
            replace_arabic_letters_pd, axis=1, args=("base_equity_symbol",)
        )
        option_data["call_name"] = option_data.apply(
            replace_arabic_letters_pd, axis=1, args=("call_name",)
        )
        option_data["call_symbol"] = option_data.apply(
            replace_arabic_letters_pd, axis=1, args=("call_symbol",)
        )
        option_data["put_symbol"] = option_data.apply(
            replace_arabic_letters_pd, axis=1, args=("put_symbol",)
        )
        option_data["put_name"] = option_data.apply(
            replace_arabic_letters_pd, axis=1, args=("put_name",)
        )

        last_market_watch_data = get_last_market_watch_data(show_traded="false")
        last_market_watch_data["blDs"] = last_market_watch_data.apply(
            rename_order_book_cols, axis=1
        )
        base_equity_data = last_market_watch_data.copy(deep=True)
        base_equity_data = base_equity_data.rename(
            columns={
                "insCode": "base_equity_ins_code",
                "lvc": "base_equity_name",
                "pdv": "base_equity_last_price",
                "hEven": "base_equity_last_update",
                "qtc": "base_equity_value",
                "blDs": "base_equity_order_book",
            }
        )
        base_equity_data["base_equity_best_buy_price"] = base_equity_data.apply(
            add_base_equity_best_orders, args=("buy_price",), axis=1
        )
        base_equity_data["base_equity_best_sell_price"] = base_equity_data.apply(
            add_base_equity_best_orders, args=("sell_price",), axis=1
        )
        base_equity_data["base_equity_best_buy_volume"] = base_equity_data.apply(
            add_base_equity_best_orders, args=("buy_volume",), axis=1
        )
        base_equity_data["base_equity_best_sell_volume"] = base_equity_data.apply(
            add_base_equity_best_orders, args=("sell_volume",), axis=1
        )

        base_equity_data = base_equity_data[
            [
                "base_equity_ins_code",
                "base_equity_name",
                "base_equity_value",
                "base_equity_last_price",
                "base_equity_best_buy_price",
                "base_equity_best_sell_price",
                "base_equity_best_buy_volume",
                "base_equity_best_sell_volume",
                "base_equity_last_update",
                "base_equity_order_book",
            ]
        ]

        option_data = pd.merge(
            left=option_data,
            right=base_equity_data,
            on="base_equity_ins_code",
            how="left",
        )

        option_data.dropna(inplace=True)

        call_data = last_market_watch_data.copy(deep=True)
        call_data = call_data.rename(
            columns={
                "insCode": "call_ins_code",
                "hEven": "call_last_update",
                "blDs": "call_order_book",
            }
        )
        call_data = call_data[["call_ins_code", "call_last_update", "call_order_book"]]
        option_data = pd.merge(
            left=option_data, right=call_data, on="call_ins_code", how="left"
        )

        put_data = last_market_watch_data.copy(deep=True)
        put_data = put_data.rename(
            columns={
                "insCode": "put_ins_code",
                "hEven": "put_last_update",
                "blDs": "put_order_book",
            }
        )
        put_data = put_data[["put_ins_code", "put_last_update", "put_order_book"]]
        option_data = pd.merge(
            left=option_data, right=put_data, on="put_ins_code", how="left"
        )

        option_data.fillna(value=60000, inplace=True)
        option_data["call_last_update"] = option_data["call_last_update"].astype(int)
        option_data["put_last_update"] = option_data["put_last_update"].astype(int)

        option_data["end_date"] = option_data.apply(
            convert_int_date_to_str_date, args=("end_date",), axis=1
        )

        option_data_dict = option_data.to_dict(orient="records")
        mongo_conn = MongodbInterface(
            db_name=OPTION_MONGO_DB, collection_name=OPTION_DATA_COLLECTION
        )
        mongo_conn.insert_docs_into_collection(option_data_dict)

        print(
            Fore.BLUE
            + f"option_data, {len(option_data_dict)} records."
            + Style.RESET_ALL
        )

        option_data = option_data[option_data["base_equity_last_price"] > 0]
        populate_all_option_strategy_async(option_data)
        # populate_all_option_strategy_sync(option_data)


def update_option_data_from_tse(run_mode: str = AUTO_MODE):

    run_main_task(
        main_task=update_option_data_from_tse_main,
        kw_args={"run_mode": run_mode},
    )
