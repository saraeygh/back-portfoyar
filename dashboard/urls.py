from django.urls import path

from dashboard.views import (
    IndustrialGroupsAPIView,
    PaperTypesAPIView,
    DollarPriceAPIView,
    BuySellValueAPIView,
    LastClosePriceAPIView,
)

dashboard_menu_urls = [
    path("industrial-groups", IndustrialGroupsAPIView.as_view()),
    path("paper-types", PaperTypesAPIView.as_view()),
]


urlpatterns = [
    path("dollar-price", DollarPriceAPIView.as_view()),
    path("buy-sell-value", BuySellValueAPIView.as_view()),
    path("last-close-price", LastClosePriceAPIView.as_view()),
] + dashboard_menu_urls
