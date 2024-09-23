from django.urls import path

from option_market.views import (
    OptionAssetNamesAPIView,
    AssetOptionSymbolsAPIView,
    SymbolHistoryAPIView,
    PriceSpreadStrategyAPIView,
    SingleSymbolVolumeStrategyAPIView,
    VolumeChangeStrategyResultAPIView,
    ProfitStatusesAPIView,
    StrategiesAPIView,
    OptionPositionsAPIView,
)

option_strategy_urls = [
    path("v2/profit-statuses/", ProfitStatusesAPIView.as_view()),
    path(
        "v2/strategies/<str:risk_level>/<str:profit_status>/",
        StrategiesAPIView.as_view(),
    ),
    path(
        "v2/positions/<str:risk_level>/<str:strategy_key>/",
        OptionPositionsAPIView.as_view(),
    ),
    path("price-spread-strategy/", PriceSpreadStrategyAPIView.as_view()),
]

option_history_urls = [
    path("option-asset-names/", OptionAssetNamesAPIView.as_view()),
    path("asset-symbols/", AssetOptionSymbolsAPIView.as_view()),
    path("symbol-history/", SymbolHistoryAPIView.as_view()),
]

volume_strategy_urls = [
    path("single-symbol-strategy/", SingleSymbolVolumeStrategyAPIView.as_view()),
    path("volume-change-strategy/", VolumeChangeStrategyResultAPIView.as_view()),
]


urlpatterns = option_history_urls + volume_strategy_urls + option_strategy_urls
