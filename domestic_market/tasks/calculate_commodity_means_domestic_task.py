from datetime import datetime, timedelta

import jdatetime
from tqdm import tqdm

from django.db.models import Sum, Avg

from core.utils import (
    MongodbInterface,
    get_deviation_percent,
    print_task_info,
    send_task_fail_success_email,
)
from core.configs import DOMESTIC_MONGO_DB

from domestic_market.models import DomesticProducer, DomesticTrade, DomesticRelation


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
            commodity_trades_in_range = producer_trades_in_range.filter(
                commodity_name=commodity_name
            )
            if commodity_trades_in_range.count() < 2:
                continue

            commodity_last_trade = commodity_trades_in_range.order_by(
                "-trade_date"
            ).first()

            domestic_mean = commodity_trades_in_range.exclude(
                id=commodity_last_trade.id
            )

            domestic_mean = (domestic_mean.aggregate(domestic_mean=Avg("close_price")))[
                "domestic_mean"
            ]

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
                    commodity_last_trade.close_price, domestic_mean
                )

            except (ZeroDivisionError, TypeError):
                continue

            shamsi_date = jdatetime.date.fromgregorian(
                date=commodity_last_trade.trade_date, locale="fa_IR"
            )

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
            }
            mean_list.append(new_record)

    if mean_list:
        mongodb = MongodbInterface(
            db_name=DOMESTIC_MONGO_DB, collection_name=collection_name
        )
        mongodb.insert_docs_into_collection(documents=mean_list)


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
    TASK_NAME = calculate_commodity_mean_domestic.__name__
    print_task_info(name=TASK_NAME)

    try:
        calculate_commodity_mean_domestic_main()
        send_task_fail_success_email(task_name=TASK_NAME)
    except Exception as e:
        send_task_fail_success_email(task_name=TASK_NAME, exception=e)

    print_task_info(color="GREEN", name=TASK_NAME)
