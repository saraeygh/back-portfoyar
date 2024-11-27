from core.configs import DOMESTIC_MONGO_DB, HEZAR_RIAL_TO_BILLION_TOMAN

from django.db.models import Sum

import jdatetime
from tqdm import tqdm
from core.utils import MongodbInterface

from domestic_market.models import DomesticMonthlySell


def calculate_end_date(start_date: jdatetime.date):
    end_date_month = start_date.month + 1 if start_date.month < 12 else 1

    end_date_year = start_date.year + 1 if end_date_month == 1 else start_date.year

    end_date = jdatetime.date(end_date_year, end_date_month, 1) - jdatetime.timedelta(
        days=1
    )

    return end_date


def next_month_start_date(start_date: jdatetime.date):
    end_date = calculate_end_date(start_date=start_date)
    next_start_date = end_date + jdatetime.timedelta(days=1)

    return next_start_date


def calculate_producer_production_sell(start_year: int, producer_id: int):

    month_name_dict = {
        1: "فروردین",
        2: "اردیبهشت",
        3: "خرداد",
        4: "تیر",
        5: "مرداد",
        6: "شهریور",
        7: "مهر",
        8: "آبان",
        9: "آذر",
        10: "دی",
        11: "بهمن",
        12: "اسفند",
    }

    production_sell = dict()
    production_sell["producer_id"] = producer_id
    production_sell["report"] = list()
    for month in range(1, 13):
        month_report = {}
        month_report["month"] = month_name_dict.get(month)
        for year in range(start_year, start_year + 2):
            month_start_date = jdatetime.date(year=year, month=month, day=1)
            month_start_date_gregorian = jdatetime.date.togregorian(month_start_date)

            month_production_sell = (
                DomesticMonthlySell.objects.filter(producer_id=producer_id)
                .filter(start_date=month_start_date_gregorian)
                .aggregate(month_sell=Sum("total_value", default=0))["month_sell"]
            )

            month_production_sell = round(
                month_production_sell / HEZAR_RIAL_TO_BILLION_TOMAN, 2
            )
            dict_key = f"{year}"
            month_report[dict_key] = month_production_sell

            month_end_date = calculate_end_date(start_date=month_start_date)
            month_start_date = month_end_date + jdatetime.timedelta(days=1)

        production_sell["report"].append(month_report)

    return production_sell


def calculate_production_sell_domestic() -> None:
    producers = DomesticMonthlySell.objects.distinct("producer").values_list(
        "producer", flat=True
    )

    current_date = jdatetime.date.today()
    start_year = current_date.year - 1

    production_sell_list = []
    for producer_id in tqdm(producers, desc="Calculate production sell", ncols=10):
        production_sell = calculate_producer_production_sell(
            start_year=start_year, producer_id=producer_id
        )
        production_sell_list.append(production_sell)

    mongodb_client = MongodbInterface(
        db_name=DOMESTIC_MONGO_DB, collection_name="producer_sell"
    )
    mongodb_client.insert_docs_into_collection(documents=production_sell_list)
