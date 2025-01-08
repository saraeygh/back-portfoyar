from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from option_market.tasks import get_option_history


class TestView(APIView):
    def get(self, request, *args, **kwargs):
        get_option_history()

        return Response({"message": "DAWWSHHAAMMI"}, status=status.HTTP_200_OK)


# COMMON
# https://cdn.tsetmc.com/api/Index/GetIndexB1LastDay/{ins_code} # Index Day history
# https://cdn.tsetmc.com/api/Index/GetIndexB2History/{ins_code} # Index whole history
# https://cdn.tsetmc.com/api/ClosingPrice/GetIndexCompany/{ins_code} # Index sub-companies

# Bourse
# https://cdn.tsetmc.com/api/MarketData/GetMarketOverview/1 # Overview
# https://cdn.tsetmc.com/api/Index/GetIndexB1LastAll/SelectedIndexes/1 # List indices
# https://cdn.tsetmc.com/api/ClosingPrice/GetTradeTop/MostVisited/1/7 # MostVisited
# https://cdn.tsetmc.com/api/Index/GetInstEffect/0/1/7 # Effects
# FaraBourse
# https://cdn.tsetmc.com/api/MarketData/GetMarketOverview/2 # Overview
# https://cdn.tsetmc.com/api/Index/GetIndexB1LastAll/SelectedIndexes/2 # List of indices
# https://cdn.tsetmc.com/api/ClosingPrice/GetTradeTop/MostVisited/2/7 # MostVisitedf
# https://cdn.tsetmc.com/api/Index/GetInstEffect/0/2/7 # Effects
