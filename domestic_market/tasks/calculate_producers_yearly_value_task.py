from celery_singleton import Singleton

from datetime import datetime, timedelta
from tqdm import tqdm
import pandas as pd

from django.db.models import Sum

from samaneh.celery import app
from core.utils import MongodbInterface, run_main_task
from core.configs import RIAL_TO_BILLION_TOMAN, DOMESTIC_MONGO_DB

from domestic_market.models import DomesticProducer, DomesticTrade
from domestic_market.serializers import GetDomesticProducerListSerailizer
from domestic_market.utils import add_value_to_name


def calculate_producers_yearly_value_main():
    ONE_YEAR_AGO = datetime.today().date() - timedelta(days=365)

    producers = list(
        DomesticTrade.objects.filter(trade_date__gt=ONE_YEAR_AGO)
        .distinct("producer")
        .values_list("producer", flat=True)
    )

    producers = DomesticProducer.objects.filter(id__in=producers)
    yearly_values = GetDomesticProducerListSerailizer(producers, many=True)
    yearly_values = pd.DataFrame(yearly_values.data)

    yearly_value_df = []
    for producer in tqdm(producers, desc="producers yearly value", ncols=10):
        yearly_value = (
            (
                DomesticTrade.objects.filter(trade_date__gt=ONE_YEAR_AGO)
                .filter(producer=producer)
                .aggregate(yearly_value=Sum("value", default=0))
            )["yearly_value"]
        ) / RIAL_TO_BILLION_TOMAN

        yearly_value_df.append({"id": producer.id, "year_value": yearly_value})
    yearly_value_df = pd.DataFrame(yearly_value_df)

    yearly_values = pd.merge(yearly_values, yearly_value_df, on="id")

    if yearly_values.empty:
        return

    yearly_values["name"] = yearly_values.apply(add_value_to_name, axis=1)
    yearly_values = yearly_values.to_dict(orient="records")

    mongo_conn = MongodbInterface(
        db_name=DOMESTIC_MONGO_DB, collection_name="producers_yearly_value"
    )
    mongo_conn.insert_docs_into_collection(documents=yearly_values)


@app.task(base=Singleton, name="calculate_producers_yearly_value_task")
def calculate_producers_yearly_value():

    run_main_task(
        main_task=calculate_producers_yearly_value_main,
        daily=True,
    )
