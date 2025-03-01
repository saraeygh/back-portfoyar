from datetime import datetime, timedelta
import jdatetime
from tqdm import tqdm
from django.db.models import Avg

from core.utils import MongodbInterface, run_main_task
from core.configs import (
    STOCK_VALUE_CHANGE_DURATION,
    STOCK_MONGO_DB,
    RIAL_TO_BILLION_TOMAN,
)

from stock_market.models import StockInstrument, StockRawHistory
from stock_market.utils import MAIN_PAPER_TYPE_DICT
from . import stock_value_change


def convert_date_obj_to_str(record):
    trade_date = record.get("trade_date")
    trade_date = str(jdatetime.date.fromgregorian(date=trade_date))
    value = record.get("value")
    record = {"x": trade_date, "y": round(value / RIAL_TO_BILLION_TOMAN, 3)}

    return record


def stock_value_history_main():
    main_paper_type = list(MAIN_PAPER_TYPE_DICT.keys())
    stocks = StockInstrument.objects.filter(paper_type__in=main_paper_type)

    today_date = datetime.today().date()
    past_date = today_date - timedelta(days=STOCK_VALUE_CHANGE_DURATION)

    duration_result_list = list()
    for stock in tqdm(stocks, desc="Value history", ncols=10):
        duration_trades = (
            StockRawHistory.objects.filter(instrument=stock)
            .filter(trade_date__gte=past_date)
            .filter(value__gt=0)
            .values("trade_date", "value")
        )

        duration_history = list(duration_trades)
        duration_history = list(map(convert_date_obj_to_str, duration_history))

        duration_mean = duration_trades.aggregate(duration_mean=Avg("value"))[
            "duration_mean"
        ]
        if duration_mean is None:
            continue

        duration_result_list.append(
            {
                "ins_code": stock.ins_code,
                "mean": duration_mean,
                "history": duration_history,
            }
        )

    mongo_conn = MongodbInterface(db_name=STOCK_MONGO_DB, collection_name="history")
    mongo_conn.insert_docs_into_collection(documents=duration_result_list)

    stock_value_change()


def stock_value_history():

    run_main_task(
        main_task=stock_value_history_main,
        daily=True,
    )
