from datetime import datetime

import pandas as pd
from tqdm import tqdm

from core.utils import MongodbInterface
from core.configs import STOCK_MONGO_DB

from stock_market.utils import HISTORY_COLUMN_RENAME
from stock_market.models import StockRawHistory, StockInstrument

from . import HISTORY_COLUMN_RENAME


DIR_COLS_LIST = [
    "open",
    "close",
    "low",
    "high",
    "close_mean",
    "yesterday_price",
]
REV_COLS_LIST = [
    "volume",
    "individual_buy_volume",
    "legal_buy_volume",
    "individual_sell_volume",
    "legal_sell_volume",
]


def trade_date_to_timestamp(row):
    trade_date = str(row.get("trade_date"))
    trade_date = datetime.strptime(trade_date, "%Y-%m-%d")
    trade_date = trade_date.timestamp()

    return trade_date


def remove_expired_adj_histories(instruments_ins_code_list):
    query = {"ins_code": {"$nin": instruments_ins_code_list}}
    mongo_conn = MongodbInterface(
        db_name=STOCK_MONGO_DB, collection_name="adjusted_history"
    )
    mongo_conn.collection.delete_many(query)


def update_stock_adjusted_history():

    model_fields_colmuns = list(HISTORY_COLUMN_RENAME.values())

    instrument_id_list = list(
        StockRawHistory.objects.distinct("instrument").values_list(
            "instrument", flat=True
        )
    )

    all_instruments = StockInstrument.objects.filter(id__in=instrument_id_list)
    instruments_ins_code_list = []
    for instrument in tqdm(all_instruments, desc="adjusted_history", ncols=10):
        raw_history = pd.DataFrame(
            StockRawHistory.objects.filter(instrument=instrument)
            .filter(trade_count__gt=0)
            .filter(yesterday_price__gt=0)
            .values(*model_fields_colmuns)
        )
        if raw_history.empty:
            continue

        raw_history.sort_values(by="trade_date", inplace=True, ascending=True)
        raw_history.reset_index(drop=True, inplace=True)

        mask = (raw_history["yesterday_price"].shift(-1) != raw_history["close_mean"])[
            :-1
        ]
        capital_changes = raw_history[:-1][mask]

        if capital_changes.empty:
            adj_history = raw_history
        else:
            adj_history = raw_history.copy(deep=True)
            for idx, _ in capital_changes.iterrows():
                current_index = idx
                next_index = current_index + 1

                current_close_mean = raw_history.iloc[current_index]["close_mean"]
                next_yesterday_price = raw_history.iloc[next_index]["yesterday_price"]

                dir_coef = next_yesterday_price / current_close_mean
                rev_coef = current_close_mean / next_yesterday_price

                adj_history.loc[0:current_index, DIR_COLS_LIST] *= dir_coef
                adj_history.loc[0:current_index, REV_COLS_LIST] *= rev_coef

                adj_history[DIR_COLS_LIST] = adj_history[DIR_COLS_LIST].astype(int)
                adj_history[REV_COLS_LIST] = adj_history[REV_COLS_LIST].astype(int)

        adj_history["trade_date"] = adj_history.apply(trade_date_to_timestamp, axis=1)
        adj_history = adj_history.to_dict(orient="records")

        query_filter = {"ins_code": f"{instrument.ins_code}"}
        mongo_conn = MongodbInterface(
            db_name=STOCK_MONGO_DB, collection_name="adjusted_history"
        )
        mongo_conn.collection.delete_one(query_filter)
        mongo_conn.collection.insert_one(
            {"ins_code": f"{instrument.ins_code}", "adjusted_history": adj_history}
        )

        instruments_ins_code_list.append(instrument.ins_code)
    # remove_expired_adj_histories(instruments_ins_code_list)
