import jdatetime as jdt

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from pymongo import DESCENDING

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import MongodbInterface
from core.configs import (
    SIXTY_SECONDS_CACHE,
    DASHBOARD_MONGO_DB,
    MARKET_MONEY_FLOW_COLLECTION,
)

MARKET_MONEY_FLOW_TABLE_HEADERS = {
    "name": "نام",
    "money_flow": "جریان پول (BT)",
    "value": "ارزش معاملات (BT)",
    "volume": "حجم معاملات (B)",
}


@method_decorator(cache_page(SIXTY_SECONDS_CACHE), name="dispatch")
class MarketMoneyFlowAPIView(APIView):
    def get(self, request):
        mongo_conn = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=MARKET_MONEY_FLOW_COLLECTION
        )
        latest_money_flow = mongo_conn.collection.find_one(sort=[("time", DESCENDING)])
        latest_money_flow.pop("_id", None)

        date = latest_money_flow.get("date")
        today_date = jdt.date.today().strftime("%Y/%m/%d")

        if date == today_date:
            table_title = "جریان پول در بازار"
        else:
            table_title = f"جریان پول در بازار {date}"

        table = {
            "table_title": table_title,
            "table_headers": MARKET_MONEY_FLOW_TABLE_HEADERS,
            "table": latest_money_flow["result"],
        }

        return Response(table, status=status.HTTP_200_OK)
