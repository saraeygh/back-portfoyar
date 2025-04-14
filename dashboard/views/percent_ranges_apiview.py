import pandas as pd
import jdatetime as jdt

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import MongodbInterface
from core.configs import (
    SIXTY_SECONDS_CACHE,
    DASHBOARD_MONGO_DB,
    CHANGE_PERCENT_RANGES,
)


@method_decorator(cache_page(SIXTY_SECONDS_CACHE), name="dispatch")
class PercentRangesAPIView(APIView):
    def get(self, request):
        mongo_conn = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=CHANGE_PERCENT_RANGES
        )
        percent_ranges = list(mongo_conn.collection.find({}, {"_id": 0}))[0]

        date = percent_ranges.get("date")
        today_date = jdt.date.today().strftime("%Y/%m/%d")
        if date == today_date:
            chart_title = "محدوده تغییرات قیمتی"
        else:
            chart_title = f"محدوده تغییرات قیمتی {date}"

        percent_ranges = percent_ranges.get("change_percent_ranges")
        percent_ranges = pd.DataFrame(percent_ranges)
        percent_ranges = percent_ranges[percent_ranges["count"] > 0]
        percent_ranges.rename(columns={"range": "x", "count": "y"}, inplace=True)

        chart = {
            "x_title": "محدوده",
            "y_title": "محدوده تغییرات",
            "chart_title": chart_title,
            "history": percent_ranges.to_dict(orient="records"),
        }

        return Response(chart, status=status.HTTP_200_OK)
