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
    TOP_OPTIONS_COLLECTION,
    DASHBOARD_TOP_5_LIMIT,
)


@method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
class OptionValueAPIView(APIView):
    def get(self, request):
        mongo_conn = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=OPTION_VALUE_ANALYSIS_COLLECTION
        )
        option_value = pd.DataFrame(
            mongo_conn.collection.find(
                {}, {"_id": 0, "time": 1, "option_value": 1, "date": 1}
            )
        )

        date = option_value.iloc[0].get("date")

        today_date = jdt.date.today().strftime("%Y/%m/%d")
        if date == today_date:
            chart_title = "ارزش کل امروز آپشن‌ها"
        else:
            chart_title = f"ارزش کل آپشن‌ها {date}"

        option_value.rename(columns={"time": "x", "option_value": "y"}, inplace=True)
        option_value.drop("date", axis=1, inplace=True)

        chart = {
            "x_title": "زمان",
            "y_title": "ارزش کل آپشن‌ها (میلیارد تومان)",
            "chart_title": chart_title,
            "history": option_value.to_dict(orient="records"),
        }

        return Response(chart, status=status.HTTP_200_OK)


@method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
class CallValueAPIView(APIView):
    def get(self, request):
        mongo_conn = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=OPTION_VALUE_ANALYSIS_COLLECTION
        )
        option_value = pd.DataFrame(
            mongo_conn.collection.find(
                {}, {"_id": 0, "time": 1, "call_value": 1, "date": 1}
            )
        )

        date = option_value.iloc[0].get("date")

        today_date = jdt.date.today().strftime("%Y/%m/%d")
        if date == today_date:
            chart_title = "ارزش کل امروز کال آپشن‌ها"
        else:
            chart_title = f"ارزش کل کال آپشن‌ها {date}"

        option_value.rename(columns={"time": "x", "call_value": "y"}, inplace=True)
        option_value.drop("date", axis=1, inplace=True)

        chart = {
            "x_title": "زمان",
            "y_title": "ارزش کل کال آپشن‌ها (میلیارد تومان)",
            "chart_title": chart_title,
            "history": option_value.to_dict(orient="records"),
        }

        return Response(chart, status=status.HTTP_200_OK)


@method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
class PutValueAPIView(APIView):
    def get(self, request):
        mongo_conn = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=OPTION_VALUE_ANALYSIS_COLLECTION
        )
        option_value = pd.DataFrame(
            mongo_conn.collection.find(
                {}, {"_id": 0, "time": 1, "put_value": 1, "date": 1}
            )
        )

        date = option_value.iloc[0].get("date")

        today_date = jdt.date.today().strftime("%Y/%m/%d")
        if date == today_date:
            chart_title = "ارزش کل امروز پوت آپشن‌ها"
        else:
            chart_title = f"ارزش کل پوت آپشن‌ها {date}"

        option_value.rename(columns={"time": "x", "put_value": "y"}, inplace=True)
        option_value.drop("date", axis=1, inplace=True)

        chart = {
            "x_title": "زمان",
            "y_title": "ارزش کل پوت آپشن‌ها (میلیارد تومان)",
            "chart_title": chart_title,
            "history": option_value.to_dict(orient="records"),
        }

        return Response(chart, status=status.HTTP_200_OK)


@method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
class CallToPutAPIView(APIView):
    def get(self, request):
        mongo_conn = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=OPTION_VALUE_ANALYSIS_COLLECTION
        )
        option_value = pd.DataFrame(
            mongo_conn.collection.find(
                {}, {"_id": 0, "time": 1, "call_to_put": 1, "date": 1}
            )
        )

        date = option_value.iloc[0].get("date")

        today_date = jdt.date.today().strftime("%Y/%m/%d")
        if date == today_date:
            chart_title = "نسبت کال به پوت امروز"
        else:
            chart_title = f"نسبت کال به پوت {date}"

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
        mongo_conn = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=OPTION_VALUE_ANALYSIS_COLLECTION
        )
        option_value = pd.DataFrame(
            mongo_conn.collection.find(
                {}, {"_id": 0, "time": 1, "option_to_market": 1, "date": 1}
            )
        )

        date = option_value.iloc[0].get("date")

        today_date = jdt.date.today().strftime("%Y/%m/%d")
        if date == today_date:
            chart_title = "نسبت امروز آپشن‌ها به کل بازار"
        else:
            chart_title = f"نسبت آپشن‌ها به کل بازار {date}"

        option_value.rename(
            columns={"time": "x", "option_to_market": "y"}, inplace=True
        )
        option_value.drop("date", axis=1, inplace=True)

        chart = {
            "x_title": "زمان",
            "y_title": "نسبت آپشن‌ها به کل بازار",
            "chart_title": chart_title,
            "history": option_value.to_dict(orient="records"),
        }

        return Response(chart, status=status.HTTP_200_OK)


@method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
class TopOptionsAPIView(APIView):
    def get(self, request):

        mongo_conn = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=TOP_OPTIONS_COLLECTION
        )
        top_options = pd.DataFrame(mongo_conn.collection.find({}, {"_id": 0}))

        if top_options.empty:
            return Response([], status=status.HTTP_200_OK)

        top_options = top_options.sort_values(by="total_value", ascending=False)
        top_options = top_options.head(DASHBOARD_TOP_5_LIMIT)
        columns_to_round = ["call_value", "put_value"]
        top_options[columns_to_round] = top_options[columns_to_round].round(3)
        top_options = top_options.to_dict(orient="records")

        return Response(top_options, status=status.HTTP_200_OK)
