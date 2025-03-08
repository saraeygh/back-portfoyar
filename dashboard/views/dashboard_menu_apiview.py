from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


from core.configs import SIXTY_MINUTES_CACHE
from stock_market.models import StockIndustrialGroup

from dashboard.serializers import IndustrialGroupSerailizer


@method_decorator(cache_page(SIXTY_MINUTES_CACHE), name="dispatch")
class IndustrialGroupsAPIView(APIView):
    def get(self, request):
        industrial_groups = StockIndustrialGroup.objects.order_by("priority").values(
            "code", "name"
        )
        industrial_groups = IndustrialGroupSerailizer(industrial_groups, many=True)

        return Response(industrial_groups.data, status=status.HTTP_200_OK)


DASHBOARD_MENU_PAPER_TYPE_LIST = [
    {"id": 1, "name": "سهام"},
    {"id": 2, "name": "بازار پایه فرابورس"},
    {"id": 8, "name": "صندوق‌های سرمایه‌گذاری"},
    {"id": 4, "name": "حق تقدم"},
    {"id": 6, "name": "اختیار معامله"},
    {"id": 7, "name": "آتی"},
]


@method_decorator(cache_page(SIXTY_MINUTES_CACHE), name="dispatch")
class PaperTypesAPIView(APIView):
    def get(self, request):
        return Response(DASHBOARD_MENU_PAPER_TYPE_LIST, status=status.HTTP_200_OK)
