import pandas as pd
import jdatetime as jdt
from datetime import datetime as dt

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import MongodbInterface
from core.configs import (
    FIVE_MINUTES_CACHE,
    DASHBOARD_MONGO_DB,
    UNWEIGHTED_INDEX_DAILY_COLLECTION,
)


@method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
class UnweightedIndexDailyAPIView(APIView):
    def get(self, request):
        mongo_conn = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB,
            collection_name=UNWEIGHTED_INDEX_DAILY_COLLECTION,
        )
        unweighted_index = pd.DataFrame(mongo_conn.collection.find({}, {"_id": 0}))

        date = str(int(unweighted_index.iloc[0].get("date")))
        date = dt.strptime(date, "%Y%m%d")
        date = jdt.date.fromgregorian(date=date.date()).strftime("%Y/%m/%d")

        today_date = jdt.date.today().strftime("%Y/%m/%d")
        change_percent = round(unweighted_index.iloc[-1].get("change_percent"), 2)
        if change_percent < 0:
            change_percent = f"٪{abs(change_percent)}-"
        else:
            change_percent = f"٪{abs(change_percent)}"

        if date == today_date:
            chart_title = f"شاخص هم‌وزن {change_percent}"
        else:
            chart_title = f"شاخص هم‌وزن {date}"

        unweighted_index.drop(columns=["date", "change_percent"], axis=1, inplace=True)
        unweighted_index.rename(
            columns={"time": "x", "current_value": "y"}, inplace=True
        )

        chart = {
            "x_title": "زمان",
            "y_title": "شاخص هم‌وزن",
            "chart_title": chart_title,
            "history": unweighted_index.to_dict(orient="records"),
        }

        return Response(chart, status=status.HTTP_200_OK)
