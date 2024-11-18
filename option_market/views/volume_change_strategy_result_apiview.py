import pandas as pd
from core.configs import SIX_HOURS_CACHE, OPTION_MONGO_DB
from core.utils import MongodbInterface, set_json_cache, get_cache_as_json
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from option_market.serializers import VolumeChangeStrategyResultSerializer


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class VolumeChangeStrategyResultAPIView(APIView):
    def post(self, request):
        volume_change_ratio = request.data.get("volume_change_ratio")
        return_period = request.data.get("return_period")
        threshold = request.data.get("threshold")
        cache_key = (
            "OPTIONS_VOLUME_CHANGE_STRATEGY"
            f"_v_{volume_change_ratio}"
            f"_r_{return_period}"
            f"_t_{threshold}"
        )
        cache_response = get_cache_as_json(cache_key)

        if cache_response is None:
            try:
                mongodb_conn = MongodbInterface(
                    db_name=OPTION_MONGO_DB,
                    collection_name="option_volume_strategy_result",
                )
                result_key = f"m_{volume_change_ratio}_d_{return_period}_t_{threshold}"
                query_filter = {"result_key": result_key}
                strategy_result = mongodb_conn.collection.find_one(
                    query_filter, {"_id": 0}
                )
                strategy_result = strategy_result["result"]

                strategy_result = pd.DataFrame(strategy_result)
                strategy_result = strategy_result.sort_values(
                    by="after_change_win_rate", ascending=False
                )
                strategy_result = strategy_result.to_dict(orient="records")

                strategy_result_srz = VolumeChangeStrategyResultSerializer(
                    strategy_result, many=True
                )

                set_json_cache(cache_key, strategy_result_srz.data, SIX_HOURS_CACHE)
                return Response(strategy_result_srz.data, status=status.HTTP_200_OK)

            except Exception:
                return Response(
                    {"message": "اطلاعات درخواستی موجود نیست."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:
            return Response(cache_response, status=status.HTTP_200_OK)
