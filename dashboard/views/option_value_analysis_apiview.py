import pandas as pd
import jdatetime as jdt

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import MongodbInterface
from core.configs import (
    FIVE_MINUTES_CACHE,
    DASHBOARD_MONGO_DB,
    OPTION_VALUE_ANALYSIS_COLLECTION,
)


@method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
class OptionValueAPIView(APIView):
    def get(self, request):
        mongo_client = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=OPTION_VALUE_ANALYSIS_COLLECTION
        )

        option_value = pd.DataFrame(
            mongo_client.collection.find(
                {}, {"_id": 0, "time": 1, "option_value": 1, "date": 1}
            )
        )

        date = option_value.iloc[0].get("date")

        today_date = jdt.date.today().strftime("%Y/%m/%d")
        if date == today_date:
            chart_title = "تغییرات امروز ارزش قراردادهای اختیار"
        else:
            chart_title = f"تغییرات ارزش قراردادهای اختیار به تاریخ {date}"

        option_value.rename(columns={"time": "x", "option_value": "y"}, inplace=True)
        option_value.drop("date", axis=1, inplace=True)

        chart = {
            "x_title": "زمان",
            "y_title": "ارزش قراردادهای اختیار (میلیارد تومان)",
            "chart_title": chart_title,
            "history": option_value.to_dict(orient="records"),
        }

        return Response(chart, status=status.HTTP_200_OK)


@method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
class CallValueAPIView(APIView):
    def get(self, request):
        mongo_client = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=OPTION_VALUE_ANALYSIS_COLLECTION
        )

        option_value = pd.DataFrame(
            mongo_client.collection.find(
                {}, {"_id": 0, "time": 1, "call_value": 1, "date": 1}
            )
        )

        date = option_value.iloc[0].get("date")

        today_date = jdt.date.today().strftime("%Y/%m/%d")
        if date == today_date:
            chart_title = "تغییرات امروز ارزش اختیارهای خرید"
        else:
            chart_title = f"تغییرات ارزش اختیارهای خرید به تاریخ {date}"

        option_value.rename(columns={"time": "x", "call_value": "y"}, inplace=True)
        option_value.drop("date", axis=1, inplace=True)

        chart = {
            "x_title": "زمان",
            "y_title": "ارزش اختیارهای خرید (میلیارد تومان)",
            "chart_title": chart_title,
            "history": option_value.to_dict(orient="records"),
        }

        return Response(chart, status=status.HTTP_200_OK)


@method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
class PutValueAPIView(APIView):
    def get(self, request):
        mongo_client = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=OPTION_VALUE_ANALYSIS_COLLECTION
        )

        option_value = pd.DataFrame(
            mongo_client.collection.find(
                {}, {"_id": 0, "time": 1, "put_value": 1, "date": 1}
            )
        )

        date = option_value.iloc[0].get("date")

        today_date = jdt.date.today().strftime("%Y/%m/%d")
        if date == today_date:
            chart_title = "تغییرات امروز ارزش اختیارهای فروش"
        else:
            chart_title = f"تغییرات ارزش اختیارهای فروش به تاریخ {date}"

        option_value.rename(columns={"time": "x", "put_value": "y"}, inplace=True)
        option_value.drop("date", axis=1, inplace=True)

        chart = {
            "x_title": "زمان",
            "y_title": "ارزش اختیارهای فروش (میلیارد تومان)",
            "chart_title": chart_title,
            "history": option_value.to_dict(orient="records"),
        }

        return Response(chart, status=status.HTTP_200_OK)


@method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
class CallToPutAPIView(APIView):
    def get(self, request):
        mongo_client = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=OPTION_VALUE_ANALYSIS_COLLECTION
        )

        option_value = pd.DataFrame(
            mongo_client.collection.find(
                {}, {"_id": 0, "time": 1, "call_to_put": 1, "date": 1}
            )
        )

        date = option_value.iloc[0].get("date")

        today_date = jdt.date.today().strftime("%Y/%m/%d")
        if date == today_date:
            chart_title = "تغییرات امروز نسبت کال به پوت"
        else:
            chart_title = f"تغییرات کال به پوت به تاریخ {date}"

        option_value.rename(columns={"time": "x", "call_to_put": "y"}, inplace=True)
        option_value.drop("date", axis=1, inplace=True)

        chart = {
            "x_title": "زمان",
            "y_title": "نسبت کال به پوت",
            "chart_title": chart_title,
            "history": option_value.to_dict(orient="records"),
        }

        return Response(chart, status=status.HTTP_200_OK)


@method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
class OptionToMarketAPIView(APIView):
    def get(self, request):
        mongo_client = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=OPTION_VALUE_ANALYSIS_COLLECTION
        )

        option_value = pd.DataFrame(
            mongo_client.collection.find(
                {}, {"_id": 0, "time": 1, "option_to_market": 1, "date": 1}
            )
        )

        date = option_value.iloc[0].get("date")

        today_date = jdt.date.today().strftime("%Y/%m/%d")
        if date == today_date:
            chart_title = "تغییرات امروز نسبت ارزش اختیارها به کل بازار"
        else:
            chart_title = f"تغییرات ارزش اختیارها به کل بازار به تاریخ {date}"

        option_value.rename(
            columns={"time": "x", "option_to_market": "y"}, inplace=True
        )
        option_value.drop("date", axis=1, inplace=True)

        chart = {
            "x_title": "زمان",
            "y_title": "نسبت ارزش اختیارها به کل بازار",
            "chart_title": chart_title,
            "history": option_value.to_dict(orient="records"),
        }

        return Response(chart, status=status.HTTP_200_OK)
