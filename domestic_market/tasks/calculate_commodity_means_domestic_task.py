from datetime import datetime, timedelta
import pandas as pd
import jdatetime as jdt
from tqdm import tqdm

from django.db.models import Sum

from core.utils import MongodbInterface, get_deviation_percent, run_main_task
from core.configs import DOMESTIC_MONGO_DB, HEZAR_RIAL_TO_MILLION_TOMAN

from domestic_market.models import DomesticProducer, DomesticTrade, DomesticRelation


def date_obj_to_str(row):
    trade_date = row.get("trade_date")
    trade_date = jdt.date.fromgregorian(date=trade_date).strftime("%Y-%m-%d")

    return trade_date


def calculate_mean(duration: int, collection_name: str, producer_id_list):
    today_date = datetime.today().date()
    start_date = today_date - timedelta(days=duration)
    one_year_ago = today_date - timedelta(days=365)

    mean_list = []
    for producer_id in tqdm(
        producer_id_list, desc=f"Domestic means - {collection_name}", ncols=10
    ):
        producer_trades_in_range = DomesticTrade.objects.filter(
            producer_id=producer_id
        ).filter(trade_date__range=(start_date, today_date))

        commodity_name_list = list(
            producer_trades_in_range.distinct("commodity_name").values_list(
                "commodity_name", flat=True
            )
        )
        for commodity_name in commodity_name_list:
            commodity_trades_in_range = (
                producer_trades_in_range.filter(commodity_name=commodity_name)
                .distinct("trade_date")
                .order_by("trade_date")
            )
            if commodity_trades_in_range.count() < 2:
                continue

            history = pd.DataFrame(
                commodity_trades_in_range.values("id", "trade_date", "close_price")
            )
            commodity_last_trade = history.iloc[-1]
            domestic_mean = history.iloc[:-1]["close_price"].mean()

            history["trade_date"] = history.apply(date_obj_to_str, axis=1)
            history.rename(
                columns={"trade_date": "x", "close_price": "y"}, inplace=True
            )
            history["y"] = history["y"] / HEZAR_RIAL_TO_MILLION_TOMAN
            history.drop("id", axis=1, inplace=True)
            history = history.to_dict(orient="records")

            try:
                producer_value_total = (
                    DomesticTrade.objects.filter(producer_id=producer_id)
                    .filter(trade_date__range=(one_year_ago, today_date))
                    .aggregate(producer_value_total=Sum("value"))[
                        "producer_value_total"
                    ]
                )

                commodity_value_total = (
                    DomesticTrade.objects.filter(producer_id=producer_id)
                    .filter(commodity_name=commodity_name)
                    .filter(trade_date__range=(one_year_ago, today_date))
                    .aggregate(commodity_value_total=Sum("value"))[
                        "commodity_value_total"
                    ]
                )

                commodity_sell_percent = (
                    commodity_value_total / producer_value_total
                ) * 100

                deviation = get_deviation_percent(
                    commodity_last_trade["close_price"], domestic_mean
                )

            except (ZeroDivisionError, TypeError):
                continue

            shamsi_date = jdt.date.fromgregorian(
                date=commodity_last_trade["trade_date"], locale="fa_IR"
            )
            id = commodity_last_trade["id"]
            commodity_last_trade = DomesticTrade.objects.get(id=id)
            link = ""
            symbol = ""
            related_stock = DomesticRelation.objects.filter(
                domestic_producer__code=commodity_last_trade.producer.code
            ).first()
            if related_stock:
                link = f"https://www.tsetmc.com/instInfo/{related_stock.stock_instrument.ins_code}"
                symbol = related_stock.stock_instrument.symbol

            new_record = {
                "producer": commodity_last_trade.producer.name,
                "producer_code": commodity_last_trade.producer.code,
                "symbol": symbol,
                "link": link,
                "commodity": commodity_last_trade.commodity_name,
                "industry": commodity_last_trade.commodity.commodity_type.industry.name,
                "commodity_type": commodity_last_trade.commodity.commodity_type.name,
                "domestic_mean": domestic_mean,
                "last_price_date": str(shamsi_date),
                "domestic_last_price": commodity_last_trade.close_price,
                "deviation": deviation,
                "commodity_sell_percent": commodity_sell_percent,
                "commodity_value_total": commodity_value_total,
                "producer_value_total": producer_value_total,
                "unit": commodity_last_trade.unit,
                "chart": {
                    "x_title": "تاریخ",
                    "y_title": "قیمت (میلیون تومان)",
                    "chart_title": f"روند تغییرات قیمت {commodity_name} در بازه انتخابی",
                    "history": history,
                },
            }
            mean_list.append(new_record)

    mongo_conn = MongodbInterface(
        db_name=DOMESTIC_MONGO_DB, collection_name=collection_name
    )
    if mean_list:
        mongo_conn.insert_docs_into_collection(documents=mean_list)
    else:
        mongo_conn.collection.delete_many({})


def calculate_commodity_mean_domestic_main():
    producer_id_list = list(DomesticProducer.objects.all().values_list("id", flat=True))
    collection_name_dict = {
        7: "one_week_mean",
        30: "one_month_mean",
        90: "three_month_mean",
        180: "six_month_mean",
        365: "one_year_mean",
    }

    for duration, collection_name in collection_name_dict.items():
        calculate_mean(duration, collection_name, producer_id_list)


def calculate_commodity_mean_domestic():

    run_main_task(
        main_task=calculate_commodity_mean_domestic_main,
        daily=True,
    )
