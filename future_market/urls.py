from django.urls import path

from future_market.views import (
    MonthlyInterestRateAPIView,
    FutureOptionPositionsAPIView,
    FutureProfitStatusesAPIView,
    FutureStrategiesAPIView,
    FuturePositionsAPIView,
)

future_urls = [
    path("monthly-interest-rate/", MonthlyInterestRateAPIView.as_view()),
    path("positions/", FuturePositionsAPIView.as_view()),
]

option_urls = [
    path("profit-statuses/", FutureProfitStatusesAPIView.as_view()),
    path(
        "strategies/<str:risk_level>/<str:profit_status>/",
        FutureStrategiesAPIView.as_view(),
    ),
    path(
        "options/<str:risk_level>/<str:strategy_key>/",
        FutureOptionPositionsAPIView.as_view(),
    ),
    # path("price-spread-strategy/", PriceSpreadStrategyAPIView.as_view()),
]

urlpatterns = future_urls + option_urls
