from datetime import datetime
import pandas as pd
from stock_market.models import StockRawHistory, StockInstrument
from . import HISTORY_COLUMN_RENAME
import warnings
from core.utils import MongodbInterface
from core.configs import STOCK_MONGO_DB
from tqdm import tqdm

warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)


def trade_date_to_timestamp(row):
    trade_date = str(row.get("trade_date"))
    trade_date = datetime.strptime(trade_date, "%Y-%m-%d")
    trade_date = trade_date.timestamp()

    return trade_date


def update_stock_adjusted_history():

    instruments = StockInstrument.objects.all()

    for instrument in tqdm(instruments, desc="adjusted_history", ncols=10):
        model_fields_colmuns = list(HISTORY_COLUMN_RENAME.values())
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
        adjusted_history = raw_history.copy(deep=True)

        adjustment_list = []
        row_count = len(raw_history)
        for i in range(1, row_count):
            previous_row = i - 1
            next_row = i
            previous_row_close_mean = raw_history.iloc[previous_row]["close_mean"]
            next_row_yesterday_price = raw_history.iloc[next_row]["yesterday_price"]
            if next_row_yesterday_price != previous_row_close_mean:
                adjustment_list.append(
                    {
                        "previous_row": previous_row,
                        "next_row": next_row,
                        "dir_coefficient": next_row_yesterday_price
                        / previous_row_close_mean,
                        "rev_coefficient": previous_row_close_mean
                        / next_row_yesterday_price,
                    }
                )

        for adjustment in adjustment_list:
            end_index = adjustment.get("previous_row")
            dir_coefficient = adjustment.get("dir_coefficient")
            rev_coefficient = adjustment.get("rev_coefficient")

            adjusted_history[
                [
                    "open",
                    "close",
                    "low",
                    "high",
                    "close_mean",
                    "yesterday_price",
                    "volume",
                    "individual_buy_volume",
                    "legal_buy_volume",
                    "individual_sell_volume",
                    "legal_sell_volume",
                ]
            ] = adjusted_history[
                [
                    "open",
                    "close",
                    "low",
                    "high",
                    "close_mean",
                    "yesterday_price",
                    "volume",
                    "individual_buy_volume",
                    "legal_buy_volume",
                    "individual_sell_volume",
                    "legal_sell_volume",
                ]
            ].astype(
                float
            )

            adjusted_history.loc[
                0:end_index,
                [
                    "open",
                    "close",
                    "low",
                    "high",
                    "close_mean",
                    "yesterday_price",
                ],
            ] *= dir_coefficient

            adjusted_history.loc[
                0:end_index,
                [
                    "volume",
                    "individual_buy_volume",
                    "legal_buy_volume",
                    "individual_sell_volume",
                    "legal_sell_volume",
                ],
            ] *= rev_coefficient

        adjusted_history = adjusted_history.round(
            {
                "open": 0,
                "close": 0,
                "low": 0,
                "high": 0,
                "close_mean": 0,
                "yesterday_price": 0,
                "volume": 0,
                "individual_buy_volume": 0,
                "legal_buy_volume": 0,
                "individual_sell_volume": 0,
                "legal_sell_volume": 0,
            }
        )

        adjusted_history["trade_date"] = adjusted_history.apply(
            trade_date_to_timestamp, axis=1
        )
        adjusted_history = adjusted_history.to_dict(orient="records")

        mongodb_conn = MongodbInterface(
            db_name=STOCK_MONGO_DB, collection_name="adjusted_history"
        )

        query_filter = {"ins_code": f"{instrument.ins_code}"}
        mongodb_conn.collection.delete_one(query_filter)
        mongodb_conn.collection.insert_one(
            {"ins_code": f"{instrument.ins_code}", "adjusted_history": adjusted_history}
        )
