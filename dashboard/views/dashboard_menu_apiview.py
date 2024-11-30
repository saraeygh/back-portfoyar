from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


from core.configs import SIXTY_MINUTES_CACHE
from stock_market.models import StockIndustrialGroup


@method_decorator(cache_page(SIXTY_MINUTES_CACHE), name="dispatch")
class IndustrialGroupsAPIView(APIView):
    def get(self, request):
        industrial_groups = StockIndustrialGroup.objects.values("code", "name")

        if industrial_groups:
            return Response(industrial_groups, status=status.HTTP_200_OK)
        return Response([], status=status.HTTP_200_OK)


DASHBOARD_MENU_PAPER_TYPE_LIST = [
    {"code": 1, "name": "سهام"},
    {"code": 2, "name": "بازار پایه فرابورس"},
    {"code": 8, "name": "صندوق‌های سرمایه‌گذاری"},
    {"code": 4, "name": "حق تقدم"},
    {"code": 6, "name": "اختیار معامله"},
    {"code": 7, "name": "آتی"},
]


@method_decorator(cache_page(SIXTY_MINUTES_CACHE), name="dispatch")
class PaperTypesAPIView(APIView):
    def get(self, request):
        return Response(DASHBOARD_MENU_PAPER_TYPE_LIST, status=status.HTTP_200_OK)
