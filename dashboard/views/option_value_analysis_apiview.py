import pandas as pd

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


# @method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
class OptionValueAPIView(APIView):
    def get(self, request):
        mongo_conn = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=OPTION_VALUE_ANALYSIS_COLLECTION
        )
        option_value = pd.DataFrame(
            mongo_conn.collection.find({}, {"_id": 0, "date": 1, "option_value": 1})
        )
        option_value.rename(columns={"date": "x", "option_value": "y"}, inplace=True)
        history = option_value.to_dict(orient="records")

        chart = {
            "x_title": "زمان",
            "y_title": "ارزش آپشن‌ها (میلیارد تومان)",
            "chart_title": f"ارزش آپشن‌ها ({history[-1]["y"]} میلیارد تومان)",
            "history": history,
        }

        return Response(chart, status=status.HTTP_200_OK)


# @method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
class CallValueAPIView(APIView):
    def get(self, request):
        mongo_conn = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=OPTION_VALUE_ANALYSIS_COLLECTION
        )
        call_value = pd.DataFrame(
            mongo_conn.collection.find({}, {"_id": 0, "date": 1, "call_value": 1})
        )

        call_value.rename(columns={"date": "x", "call_value": "y"}, inplace=True)
        history = call_value.to_dict(orient="records")

        chart = {
            "x_title": "زمان",
            "y_title": "ارز کال آپشن‌ها (میلیارد تومان)",
            "chart_title": f"ارزش کال آپشن‌ها ({history[-1]["y"]} میلیارد تومان)",
            "history": history,
        }

        return Response(chart, status=status.HTTP_200_OK)


# @method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
class PutValueAPIView(APIView):
    def get(self, request):
        mongo_conn = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=OPTION_VALUE_ANALYSIS_COLLECTION
        )
        put_value = pd.DataFrame(
            mongo_conn.collection.find({}, {"_id": 0, "date": 1, "put_value": 1})
        )

        put_value.rename(columns={"date": "x", "put_value": "y"}, inplace=True)
        history = put_value.to_dict(orient="records")

        chart = {
            "x_title": "زمان",
            "y_title": "ارزش پوت آشپن‌ها (میلیارد تومان)",
            "chart_title": f"ارزش پوت آپشن‌ها ({history[-1]["y"]} میلیارد تومان)",
            "history": history,
        }

        return Response(chart, status=status.HTTP_200_OK)


# @method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
class PutToCallAPIView(APIView):
    def get(self, request):
        mongo_conn = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=OPTION_VALUE_ANALYSIS_COLLECTION
        )
        put_to_call = pd.DataFrame(
            mongo_conn.collection.find({}, {"_id": 0, "date": 1, "put_to_call": 1})
        )

        put_to_call.rename(columns={"date": "x", "put_to_call": "y"}, inplace=True)
        history = put_to_call.to_dict(orient="records")

        chart = {
            "x_title": "زمان",
            "y_title": "نسبت پوت به کال",
            "chart_title": f"نسبت پوت به کال ({history[-1]["y"]})",
            "history": history,
        }

        return Response(chart, status=status.HTTP_200_OK)


# @method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
class OptionToMarketAPIView(APIView):
    def get(self, request):
        mongo_conn = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=OPTION_VALUE_ANALYSIS_COLLECTION
        )
        option_to_market = pd.DataFrame(
            mongo_conn.collection.find({}, {"_id": 0, "date": 1, "option_to_market": 1})
        )

        option_to_market.rename(
            columns={"date": "x", "option_to_market": "y"}, inplace=True
        )
        history = option_to_market.to_dict(orient="records")

        chart = {
            "x_title": "زمان",
            "y_title": "ارزش آپشن‌ها به کل بازار",
            "chart_title": f"ارزش آپشن‌ها به کل بازار ({history[-1]["y"]})",
            "history": history,
        }

        return Response(chart, status=status.HTTP_200_OK)


# @method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
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
