import jdatetime
from datetime import datetime, timedelta

from core.configs import GLOBAL_MONGO_DB

from tqdm import tqdm
from core.utils import MongodbInterface, get_deviation_percent
from django.db.models import Avg
from global_market.models import GlobalCommodity, GlobalTrade


def calculate_mean(duration: int, collection_name: str, commodity_id_list):
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=duration)

    mean_list = []
    for commodity_id in tqdm(
        commodity_id_list, desc=f"Global ({collection_name})", ncols=10
    ):
        commodity_trades_in_range = GlobalTrade.objects.filter(
            commodity_id=commodity_id
        ).filter(trade_date__range=(start_date, end_date))

        transit_id_list = list(
            commodity_trades_in_range.distinct("transit").values_list(
                "transit", flat=True
            )
        )
        for transit_id in transit_id_list:

            transit_trades_in_range = commodity_trades_in_range.filter(
                transit_id=transit_id
            )
            if transit_trades_in_range.count() < 2:
                continue

            transit_last_trade = (
                transit_trades_in_range.order_by("-trade_date")
                .select_related("commodity__commodity_type__industry")
                .first()
            )

            global_mean = transit_trades_in_range.exclude(id=transit_last_trade.id)
            global_mean = transit_trades_in_range.aggregate(global_mean=Avg("price"))[
                "global_mean"
            ]

            try:
                deviation = get_deviation_percent(transit_last_trade.price, global_mean)
            except (ZeroDivisionError, TypeError):
                continue

            new_record = {
                "industry": transit_last_trade.commodity.commodity_type.industry.name,
                "commodity_type": transit_last_trade.commodity.commodity_type.name,
                "commodity": transit_last_trade.commodity.name,
                "transit": transit_last_trade.transit.transit_type,
                "global_mean": float(global_mean),
                "last_price_date": str(
                    jdatetime.date.fromgregorian(date=transit_last_trade.trade_date)
                ),
                "global_last_price": float(transit_last_trade.price),
                "deviation": float(deviation),
            }

            mean_list.append(new_record)

    mongodb = MongodbInterface(db_name=GLOBAL_MONGO_DB, collection_name=collection_name)
    if mean_list:
        mongodb.insert_docs_into_collection(documents=mean_list)
    else:
        mongodb.collection.delete_many({})


def calculate_commodity_means_global():
    commodity_id_list = list(GlobalCommodity.objects.all().values_list("id", flat=True))

    collection_name_dict = {
        7: "one_week_mean",
        30: "one_month_mean",
        90: "three_month_mean",
        180: "six_month_mean",
        365: "one_year_mean",
    }

    for duration, collection_name in collection_name_dict.items():
        calculate_mean(duration, collection_name, commodity_id_list)

    return
