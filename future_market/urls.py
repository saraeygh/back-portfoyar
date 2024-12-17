from django.urls import path

from future_market.views import (
    MonthlyInterestRateAPIView,
    FutureOptionPositionsAPIView,
    FuturePositionsAPIView,
)
from option_market.views import ProfitStatusesAPIView, StrategiesAPIView

future_urls = [
    path("monthly-interest-rate/", MonthlyInterestRateAPIView.as_view()),
    path("positions/", FuturePositionsAPIView.as_view()),
]

option_urls = [
    path("profit-statuses/", ProfitStatusesAPIView.as_view()),
    path(
        "strategies/<str:risk_level>/<str:profit_status>/",
        StrategiesAPIView.as_view(),
    ),
    path(
        "options/<str:risk_level>/<str:strategy_key>/",
        FutureOptionPositionsAPIView.as_view(),
    ),
]

urlpatterns = future_urls + option_urls
