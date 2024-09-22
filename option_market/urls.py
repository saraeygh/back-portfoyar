from django.urls import path

from option_market.views import (
    StrategyAPIView,
    StrategyOptionsAPIView,
    OptionAssetNamesAPIView,
    AssetOptionSymbolsAPIView,
    SymbolHistoryAPIView,
    PriceSpreadStrategyAPIView,
    SingleSymbolVolumeStrategyAPIView,
    VolumeChangeStrategyResultAPIView,
    ProfitStatusListAPIView,
    RiskLevelListAPIView,
    FilteredStrategyListAPIView,
    PositionsAPIView,
    StrategyListAPIView,
    StrategyResultAPIView,
    ProfitStatusesAPIView,
    StrategiesAPIView,
    OptionPositionsAPIView,
)

option_urls = [
    path("option-asset-names/", OptionAssetNamesAPIView.as_view()),
    path("asset-symbols/", AssetOptionSymbolsAPIView.as_view()),
    path("symbol-history/", SymbolHistoryAPIView.as_view()),
]

strategy_urls = [
    path("strategy/", StrategyAPIView.as_view()),
    path("strategy/<str:collection_key>/", StrategyOptionsAPIView.as_view()),
    path("price-spread-strategy/", PriceSpreadStrategyAPIView.as_view()),
    path("single-symbol-strategy/", SingleSymbolVolumeStrategyAPIView.as_view()),
    path("volume-change-strategy/", VolumeChangeStrategyResultAPIView.as_view()),
]

new_option_strategy_urls = [
    # NEW VERSION
    path("v2/profit-statuses/", ProfitStatusesAPIView.as_view()),
    path(
        "v2/strategies/<str:risk_level>/<str:profit_status>/",
        StrategiesAPIView.as_view(),
    ),
    path(
        "v2/positions/<str:risk_level>/<str:strategy_key>/",
        OptionPositionsAPIView.as_view(),
    ),
    #
    #
    #
    # OLD VERSION
    path("profit-statuses/", ProfitStatusListAPIView.as_view()),
    path("risk-levels/<str:profit_status>/", RiskLevelListAPIView.as_view()),
    path("strategies/<str:risk_level>/", FilteredStrategyListAPIView.as_view()),
    path("positions/<str:risk_level>/<str:strategy_key>/", PositionsAPIView.as_view()),
    #
    #
    #
    # OLDEST VERSION
    path("strategy-list/", StrategyListAPIView.as_view()),
    path("<str:strategy_key>/", StrategyResultAPIView.as_view()),
]

urlpatterns = option_urls + strategy_urls + new_option_strategy_urls
