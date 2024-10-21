from django.urls import path

from future_market.views import (
    MonthlyInterestRateAPIView,
    FuturePositionsAPIView,
    FutureOptionPositionsAPIView,
)

future_urls = [
    path("monthly-interest-rate/", MonthlyInterestRateAPIView.as_view()),
    path("positions/", FuturePositionsAPIView.as_view()),
    #
    # path("v2/profit-statuses/", ProfitStatusesAPIView.as_view()),
    # path(
    #     "v2/strategies/<str:risk_level>/<str:profit_status>/",
    #     StrategiesAPIView.as_view(),
    # ),
    path(
        "options/<str:risk_level>/<str:strategy_key>/",
        FutureOptionPositionsAPIView.as_view(),
    ),
    # path("price-spread-strategy/", PriceSpreadStrategyAPIView.as_view()),
]

urlpatterns = future_urls
