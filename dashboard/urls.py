from django.urls import path

from dashboard.views import (
    BuySellValueAPIView,
    IndustrialGroupsAPIView,
    PaperTypesAPIView,
    MarketWatchDashboardAPIView,
)

dashboard_menu_urls = [
    path("industrial-groups/", IndustrialGroupsAPIView.as_view()),
    path("paper-types/", PaperTypesAPIView.as_view()),
]

stock_market_dashboard_urls = [
    path("marketwatch/", MarketWatchDashboardAPIView.as_view()),
]

urlpatterns = (
    [
        path("buy-sell-value/", BuySellValueAPIView.as_view()),
    ]
    + dashboard_menu_urls
    + stock_market_dashboard_urls
)
