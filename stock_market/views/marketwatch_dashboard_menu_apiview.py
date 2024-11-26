import pandas as pd
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


from core.configs import SIXTY_SECONDS_CACHE, STOCK_MONGO_DB, MARKET_WATCH_TOP_5_LIMIT
from core.utils import MongodbInterface, add_index_as_id

from stock_market.utils import MAIN_PAPER_TYPE_DICT
from dashboard.utils import STOCK_MARKET_WATCH_INDICES, OPTION_MARKET_WATCH_INDICES


@method_decorator(cache_page(SIXTY_SECONDS_CACHE), name="dispatch")
class StockDashboardAPIView(APIView):
    def get(self, request):

        result = dict()
        for index, index_serializer in STOCK_MARKET_WATCH_INDICES.items():
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


# @method_decorator(cache_page(SIXTY_SECONDS_CACHE), name="dispatch")
class OptionDashboardAPIView(APIView):
    def get(self, request):

        result = dict()
        for index, index_serializer in OPTION_MARKET_WATCH_INDICES.items():
            mongo_client = MongodbInterface(
                db_name=STOCK_MONGO_DB, collection_name=index
            )
            index_result = mongo_client.collection.find({}, {"_id": 0})
            index_result = pd.DataFrame(index_result)

            if index_result.empty:
                result[index] = []
                continue

            if index == "option_price_spread":
                index_result = index_result.sort_values(
                    by="price_spread", ascending=False
                )
            else:
                index_result = index_result.sort_values(
                    by="value_change", ascending=False
                )

            index_result = index_result.head(MARKET_WATCH_TOP_5_LIMIT)
            index_result.reset_index(drop=True, inplace=True)
            index_result["id"] = index_result.apply(add_index_as_id, axis=1)
            index_result = index_result.to_dict(orient="records")
            index_result = index_serializer(index_result, many=True)
            result[index] = index_result.data

        return Response(result, status=status.HTTP_200_OK)
