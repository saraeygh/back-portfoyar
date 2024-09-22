from core.configs import FIVE_MINUTES_CACHE
from core.utils import set_json_cache, get_cache_as_json

from option_market.serializers import SingleSymbolVlomueStrategySerializer
from option_market.utils import (
    match_strategy_for_single_symbol,
    prepare_history_data_for_strategy,
)
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class SingleSymbolVolumeStrategyAPIView(APIView):
    def post(self, request):
        symbol = request.data.get("symbol")
        volume_change_ratio = request.data.get("volume_change_ratio")
        return_period = request.data.get("return_period")
        threshold = request.data.get("threshold")

        cache_key = (
            "OPTIONS_SINGLE_SYMBOL_STRATEGY"
            f"_s_{symbol}"
            f"_v_{volume_change_ratio}"
            f"_r_{return_period}"
            f"_t_{threshold}"
        )
        cache_response = get_cache_as_json(cache_key)

        if cache_response is None:
            collection_history_df, _ = prepare_history_data_for_strategy(symbol=symbol)

            number_of_rows = collection_history_df.shape[0]
            if number_of_rows < return_period:
                return Response(
                    {"message": "نتیجه‌ای یافت نشد."}, status=status.HTTP_400_BAD_REQUEST
                )

            (matched_strategy_list, _, _, _, _, _, _) = (
                match_strategy_for_single_symbol(
                    symbol_history_df=collection_history_df,
                    on_change_mean_of_max_comulative_return_percent_list=[],
                    on_change_day_to_max_return_percent_list=[],
                    after_change_mean_of_max_comulative_return_percent_list=[],
                    after_change_day_to_max_return_percent_list=[],
                    volume_change_ratio=volume_change_ratio,
                    return_period=return_period,
                    threshold=threshold,
                )
            )

            single_symbol_strategy_srz = SingleSymbolVlomueStrategySerializer(
                matched_strategy_list, many=True
            )

            set_json_cache(
                cache_key, single_symbol_strategy_srz.data, FIVE_MINUTES_CACHE
            )
            return Response(single_symbol_strategy_srz.data, status=status.HTTP_200_OK)

        else:
            return Response(cache_response, status=status.HTTP_200_OK)
