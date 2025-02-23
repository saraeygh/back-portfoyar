import pandas as pd

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.configs import STOCK_MONGO_DB, SIXTY_SECONDS_CACHE, STOCK_TOP_500_LIMIT
from core.utils import (
    MongodbInterface,
    ALL_TABLE_COLS,
    TABLE_COLS_QP,
    SUMMARY_TABLE_COLS,
    add_index_as_id,
)

from stock_market.utils import MAIN_PAPER_TYPE_DICT
from stock_market.permissions import HasStockSubscription
from stock_market.serializers import (
    SummaryPersonBuyPressureSerailizer,
    PersonBuyPressureSerailizer,
)


@method_decorator(cache_page(SIXTY_SECONDS_CACHE), name="dispatch")
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasStockSubscription])
class StockPersonBuyPressureAPIView(APIView):
    def get(self, request):
        mongo_conn = MongodbInterface(
            db_name=STOCK_MONGO_DB, collection_name="buy_pressure"
        )
        results = mongo_conn.collection.find(
            {"paper_type": {"$in": list(MAIN_PAPER_TYPE_DICT.keys())}}, {"_id": 0}
        )
        results = pd.DataFrame(results)
        mongo_conn.client.close()
        if results.empty:
            return Response(
                {"message": "مشکل در درخواست"}, status=status.HTTP_400_BAD_REQUEST
            )

        results = results[~results["symbol"].str.contains(r"\d")]
        results = results.drop_duplicates(subset=["symbol"], keep="first")
        results = results.sort_values(by="buy_pressure", ascending=False)
        results = results.head(STOCK_TOP_500_LIMIT)
        results.reset_index(drop=True, inplace=True)
        results["id"] = results.apply(add_index_as_id, axis=1)
        results = results.to_dict(orient="records")

        table = request.query_params.get(TABLE_COLS_QP, SUMMARY_TABLE_COLS)
        if table == ALL_TABLE_COLS:
            results = PersonBuyPressureSerailizer(results, many=True)
        else:
            results = SummaryPersonBuyPressureSerailizer(results, many=True)

        return Response(results.data, status=status.HTTP_200_OK)
