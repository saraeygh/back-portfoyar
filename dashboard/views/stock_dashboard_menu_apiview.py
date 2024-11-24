import pandas as pd
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


from core.configs import SIXTY_SECONDS_CACHE, STOCK_MONGO_DB, MARKET_WATCH_TOP_5_LIMIT
from core.utils import MongodbInterface, add_index_as_id

from stock_market.utils import MAIN_PAPER_TYPE_DICT
from stock_market.serializers import (
    PersonMoneyFlowSerailizer,
    PersonBuyPressureSerailizer,
    PersonBuyValueSerailizer,
    StockValueChangeSerailizer,
    BuyOrderRatioSerailizer,
    SellOrderRatioSerailizer,
)

MARKET_WATCH_INDICES = {
    "money_flow": PersonMoneyFlowSerailizer,
    "buy_pressure": PersonBuyPressureSerailizer,
    "buy_value": PersonBuyValueSerailizer,
    "value_change": StockValueChangeSerailizer,
    "buy_ratio": BuyOrderRatioSerailizer,
    "sell_ratio": SellOrderRatioSerailizer,
}


@method_decorator(cache_page(SIXTY_SECONDS_CACHE), name="dispatch")
class MarketWatchDashboardAPIView(APIView):
    def get(self, request):

        result = dict()
        for index, index_serializer in MARKET_WATCH_INDICES.items():
            mongo_client = MongodbInterface(
                db_name=STOCK_MONGO_DB, collection_name=index
            )
            index_result = mongo_client.collection.find(
                {"paper_type": {"$in": list(MAIN_PAPER_TYPE_DICT.keys())}}, {"_id": 0}
            )
            index_result = pd.DataFrame(index_result)

            if index_result.empty:
                result[index] = []
                continue

            index_result = index_result[~index_result["symbol"].str.contains(r"\d")]
            index_result = index_result.drop_duplicates(subset=["symbol"], keep="first")
            index_result = index_result.sort_values(by=index, ascending=False)
            index_result = index_result.head(MARKET_WATCH_TOP_5_LIMIT)
            index_result.reset_index(drop=True, inplace=True)
            index_result["id"] = index_result.apply(add_index_as_id, axis=1)
            index_result = index_result.to_dict(orient="records")

            index_result = index_serializer(index_result, many=True)
            result[index] = index_result.data

        return Response(result, status=status.HTTP_200_OK)
