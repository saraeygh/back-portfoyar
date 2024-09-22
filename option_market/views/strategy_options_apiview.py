from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from core.configs import SIXTY_SECONDS_CACHE, TO_MILLION
from core.utils import add_index_as_id

from django.shortcuts import get_object_or_404
from option_market.models import Strategy
from option_market.utils import get_strategy_result, convert_int_date_to_str_date
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@method_decorator(cache_page(SIXTY_SECONDS_CACHE), name="dispatch")
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class StrategyOptionsAPIView(APIView):
    def get(self, request, collection_key):
        strategy = get_object_or_404(Strategy, collection_key=collection_key)

        result = get_strategy_result(collection_key=strategy.collection_key)

        if collection_key == "covered_calls":
            result = result[result["base_equit_price"] >= 0.9 * result["strike"]]

        result["expiration_date"] = result.apply(
            convert_int_date_to_str_date, args=("expiration_date",), axis=1
        )
        result["value"] = result["value"] / TO_MILLION
        result.reset_index(drop=True, inplace=True)
        result["id"] = result.apply(add_index_as_id, axis=1)
        first_column = result.pop("id")
        result.insert(0, "id", first_column)
        result["value"] = result["value"].astype(int)
        result = result.to_dict(orient="records")

        return Response(data=result)
