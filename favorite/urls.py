from django.urls import path

from favorite.views import (
    DomesticFavoritePriceChartByProducerAPIView,
    DomesticFavoriteRatioChartByProducerAPIView,
    DomesticFavoritePriceChartByCategoryAPIView,
    DomesticFavoriteRatioChartByCategoryAPIView,
    DomesticFavoriteProducerReportAPIView,
    GlobalFavoritePriceChartAPIView,
    GlobalFavoriteRatioChartAPIView,
    # OptionsFavoriteSymbolAPIView,
    StockFavoriteROIGroupAPIView,
    StockFavoriteROIInstrumentAPIView,
    StockFavoriteROIInstrumentListAPIView,
)


domestic_favorites_urls = [
    # PRODUCER URLs
    path(
        "domestic-price/producer/",
        DomesticFavoritePriceChartByProducerAPIView.as_view(),
    ),
    path(
        "domestic-price/producer/<int:favorite_id>",
        DomesticFavoritePriceChartByProducerAPIView.as_view(),
    ),
    path(
        "domestic-ratio/producer/",
        DomesticFavoriteRatioChartByProducerAPIView.as_view(),
    ),
    path(
        "domestic-ratio/producer/<int:favorite_id>",
        DomesticFavoriteRatioChartByProducerAPIView.as_view(),
    ),
    # CATEGORY URLs
    path(
        "domestic-price/category/",
        DomesticFavoritePriceChartByCategoryAPIView.as_view(),
    ),
    path(
        "domestic-price/category/<int:favorite_id>",
        DomesticFavoritePriceChartByCategoryAPIView.as_view(),
    ),
    path(
        "domestic-ratio/category/",
        DomesticFavoriteRatioChartByCategoryAPIView.as_view(),
    ),
    path(
        "domestic-ratio/category/<int:favorite_id>",
        DomesticFavoriteRatioChartByCategoryAPIView.as_view(),
    ),
    # PRODUCER SELL URLs
    path(
        "domestic-production/",
        DomesticFavoriteProducerReportAPIView.as_view(),
    ),
    path(
        "domestic-production/<int:favorite_id>",
        DomesticFavoriteProducerReportAPIView.as_view(),
    ),
]


global_favorites_urls = [
    path("global-favorite-price-chart/", GlobalFavoritePriceChartAPIView.as_view()),
    path(
        "global-favorite-price-chart/<int:favorite_price_chart_id>",
        GlobalFavoritePriceChartAPIView.as_view(),
    ),
    path("global-favorite-ratio-chart/", GlobalFavoriteRatioChartAPIView.as_view()),
    path(
        "global-favorite-ratio-chart/<int:favorite_ratio_chart_id>",
        GlobalFavoriteRatioChartAPIView.as_view(),
    ),
]

options_favorites_urls = [
    # path(
    #     "favorite-option-symbol/<str:collection_key>/",
    #     OptionsFavoriteSymbolAPIView.as_view(),
    # ),
    # path(
    #     "favorite-option-symbol/<str:collection_key>/<str:symbol>/",
    #     OptionsFavoriteSymbolAPIView.as_view(),
    # ),
]

stock_favorite_urls = [
    path("favorite-roi-groups/", StockFavoriteROIGroupAPIView.as_view()),
    path(
        "favorite-roi-groups/<int:favorite_id>", StockFavoriteROIGroupAPIView.as_view()
    ),
    path(
        "favorite-roi-instruments/",
        StockFavoriteROIInstrumentListAPIView.as_view(),
    ),
    path(
        "favorite-roi-instruments/<int:group_id>",
        StockFavoriteROIInstrumentAPIView.as_view(),
    ),
    path(
        "favorite-roi-instruments/<int:group_id>/<str:symbol>",
        StockFavoriteROIInstrumentAPIView.as_view(),
    ),
]

urlpatterns = (
    domestic_favorites_urls
    + global_favorites_urls
    + options_favorites_urls
    + stock_favorite_urls
)
