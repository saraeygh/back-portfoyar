from django.urls import path

from dashboard.views import (
    IndustrialGroupsAPIView,
    PaperTypesAPIView,
    DollarPriceAPIView,
    BuySellValueAPIView,
    LastClosePriceAPIView,
    TotalIndexDailyAPIView,
    UnweightedIndexDailyAPIView,
)

dashboard_menu_urls = [
    path("industrial-groups", IndustrialGroupsAPIView.as_view()),
    path("paper-types", PaperTypesAPIView.as_view()),
]


urlpatterns = [
    path("total-index-daily", TotalIndexDailyAPIView.as_view()),
    path("unweighted-index-daily", UnweightedIndexDailyAPIView.as_view()),
    path("buy-sell-value", BuySellValueAPIView.as_view()),
    path("last-close-price", LastClosePriceAPIView.as_view()),
    path("dollar-price", DollarPriceAPIView.as_view()),
] + dashboard_menu_urls
