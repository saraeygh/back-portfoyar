from core.configs import THIRTY_MINUTES_CACHE, STOCK_TOP_100_LIMIT

from core.utils import add_index_as_id, set_json_cache, get_cache_as_json
from stock_market.models.recommendation_config_model import RELATED_NAMES
from stock_market.serializers import StockRecommendedSerailizer
from stock_market.utils import stock_recommendation, get_recommendation_config
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class StockRecommendedAPIView(APIView):

    def get(self, request):
        config = get_recommendation_config(user=request.user)
        if config is None:
            return Response([], status=status.HTTP_200_OK)

        updated_at = config.updated_at.strftime("%H-%M-%S")
        cache_key = (
            "STOCK_RECOMMENDATION_RESULT"
            f"_config_id_{config.id}"
            f"_updated_at_{updated_at}"
        )
        for related_name in RELATED_NAMES:
            updated_at = getattr(config, related_name).updated_at.strftime("%H-%M-%S")
            cache_key = cache_key + updated_at + "-"

        cache_response = get_cache_as_json(cache_key)

        if cache_response is None:
            results = stock_recommendation(config=config)
            if results.empty:
                return Response([], status=status.HTTP_200_OK)

            results = results.sort_values(by="total_score", ascending=False)
            results = results.head(STOCK_TOP_100_LIMIT)
            results.reset_index(drop=True, inplace=True)
            results["id"] = results.apply(add_index_as_id, axis=1)
            results.dropna(inplace=True)
            results = results.to_dict(orient="records")
            results = StockRecommendedSerailizer(results, many=True)

            set_json_cache(cache_key, results.data, THIRTY_MINUTES_CACHE)
            return Response(results.data, status=status.HTTP_200_OK)
        else:
            return Response(cache_response, status=status.HTTP_200_OK)
