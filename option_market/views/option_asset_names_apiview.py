import pandas as pd
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from core.configs import SIXTY_SECONDS_CACHE

from core.utils import RedisInterface
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@method_decorator(cache_page(SIXTY_SECONDS_CACHE), name="dispatch")
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class OptionAssetNamesAPIView(APIView):
    def get(self, request):

        redis_conn = RedisInterface(db=3)
        option_base_equity = pd.DataFrame(
            redis_conn.get_list_of_dicts(list_key="option_data")
        )
        option_base_equity.sort_values(by="base_equity_symbol", inplace=True)
        option_base_equity = option_base_equity["base_equity_symbol"].unique().tolist()

        return Response(option_base_equity)
