from celery_singleton import Singleton

from datetime import datetime, timedelta

import pandas as pd
import jdatetime as jdt

from django.db.models import Q

from samaneh.celery import app

from core.utils import MongodbInterface, run_main_task
from core.configs import (
    STOCK_VALUE_CHANGE_DURATION,
    STOCK_MONGO_DB,
    OPTION_MONGO_DB,
    OPTION_DATA_COLLECTION,
    RIAL_TO_MILLION_TOMAN,
)

from stock_market.models import StockRawHistory
from stock_market.utils import CALL_OPTION, PUT_OPTION
from . import stock_option_value_change


def stock_option_value_history_main():

    today_date = datetime.today().date()
    past_date = today_date - timedelta(days=STOCK_VALUE_CHANGE_DURATION)

    option_history = pd.DataFrame(
        (
            StockRawHistory.objects.filter(trade_date__gte=past_date)
            .filter(value__gt=0)
            .filter(
                Q(instrument__name__startswith="اختیارخ")
                | Q(instrument__name__startswith="اختیارف")
            )
            .values("instrument__ins_code", "trade_date", "value")
        )
    )
    mongo_conn = MongodbInterface(
        db_name=OPTION_MONGO_DB, collection_name=OPTION_DATA_COLLECTION
    )
    last_option = pd.DataFrame(mongo_conn.collection.find({}, {"_id": 0}))

    last_option = last_option[
        [
            "call_ins_code",
            "call_symbol",
            "put_ins_code",
            "put_symbol",
            "base_equity_ins_code",
            "base_equity_symbol",
        ]
    ]
    option_types = [CALL_OPTION, PUT_OPTION]
    for option_type in option_types:
        right_on = "call_ins_code"
        if option_type == PUT_OPTION:
            right_on = "put_ins_code"

        options = pd.merge(
            left=option_history,
            right=last_option,
            left_on="instrument__ins_code",
            right_on=right_on,
            how="left",
        )
        options.dropna(inplace=True)

        base_equities = options["base_equity_symbol"].unique().tolist()
        option_value_mean_history = []
        for base_equity in base_equities:
            base_equity_value_history = {
                "symbol": base_equity,
                "chart": {
                    "x_title": "تاریخ",
                    "y_title": "میانگین ارزش (میلیون تومان)",
                    "chart_title": "روند ماهانه تغییرات ارزش آپشن‌ها",
                    "history": [],
                },
            }
            base_equity_options: pd.DataFrame = options.loc[
                options["base_equity_symbol"] == base_equity
            ]

            trade_dates = sorted(base_equity_options["trade_date"].unique().tolist())
            for trade_date in trade_dates:
                trade_date_options: pd.DataFrame = base_equity_options.loc[
                    options["trade_date"] == trade_date
                ]
                new_history = {
                    "x": str(jdt.date.fromgregorian(date=trade_date)),
                    "y": round(
                        float(trade_date_options["value"].mean())
                        / RIAL_TO_MILLION_TOMAN,
                        3,
                    ),
                }
                base_equity_value_history["chart"]["history"].append(new_history)
            option_value_mean_history.append(base_equity_value_history)

        if option_value_mean_history:
            if option_type == CALL_OPTION:
                collection_name = "call_value_history"
            else:
                collection_name = "put_value_history"

            mongo_conn = MongodbInterface(
                db_name=STOCK_MONGO_DB, collection_name=collection_name
            )
            mongo_conn.insert_docs_into_collection(documents=option_value_mean_history)

    stock_option_value_change()


@app.task(base=Singleton, name="stock_option_value_history_task")
def stock_option_value_history():

    run_main_task(
        main_task=stock_option_value_history_main,
        daily=True,
    )
