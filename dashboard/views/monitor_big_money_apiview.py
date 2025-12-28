from datetime import datetime as dt

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

import pandas as pd
from pymongo import DESCENDING

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import MongodbInterface, get_relative_datetime
from core.configs import (
    SIXTY_SECONDS_CACHE,
    STOCK_MONGO_DB,
    BIG_MONEY_ALERTS_COLLECTION,
)


def relative_datetime(row):
    date = row.get("last_date")
    year, month, day = map(int, date.split("/"))
    time = str(int(row.get("last_time")))
    if len(time) != 6:
        time = "0" + time
    hour, minute, second = int(time[0:2]), int(time[2:4]), int(time[4:6])

    relative_datetime = get_relative_datetime(
        dt(year, month, day, hour, minute, second)
    )

    return relative_datetime


# @method_decorator(cache_page(SIXTY_SECONDS_CACHE), name="dispatch")
class BigMoneyAPIView(APIView):
    def get(self, request):
        mongo_conn = MongodbInterface(
            db_name=STOCK_MONGO_DB, collection_name=BIG_MONEY_ALERTS_COLLECTION
        )
        latest_big_money = pd.DataFrame(
            list(
                mongo_conn.collection.find(
                    {},
                    {"_id": 0},
                    sort=[("last_date", DESCENDING), ("last_time", DESCENDING)],
                )
            )
        )

        latest_big_money["time"] = latest_big_money.apply(relative_datetime, axis=1)
        latest_big_money = latest_big_money[
            [
                "symbol",
                "name",
                "buy_value_diff",
                "sell_value_diff",
                "buy_count_diff",
                "sell_count_diff",
                "side",
                "time",
            ]
        ]
        latest_big_money = latest_big_money.to_dict(orient="records")

        return Response(latest_big_money, status=status.HTTP_200_OK)
