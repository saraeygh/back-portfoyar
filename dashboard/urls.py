from django.urls import path

from dashboard.views import (
    IndustrialGroupsAPIView,
    PaperTypesAPIView,
    DollarPriceAPIView,
    BuySellValueAPIView,
    LastClosePriceAPIView,
    TotalIndexDailyAPIView,
    UnweightedIndexDailyAPIView,
    OptionValueAPIView,
    CallValueAPIView,
    PutValueAPIView,
    CallToPutAPIView,
    OptionToMarketAPIView,
    DomesticMeanDeviationAPIView,
    GlobalMeanDeviationAPIView,
    IndustryROIAPIView,
    MinimumPEAPIView,
)

dashboard_menu_urls = [
    path("industrial-groups", IndustrialGroupsAPIView.as_view()),
    path("paper-types", PaperTypesAPIView.as_view()),
]

index_urls = [
    path("total-index-daily", TotalIndexDailyAPIView.as_view()),
    path("unweighted-index-daily", UnweightedIndexDailyAPIView.as_view()),
]

option_urls = [
    path("option-value", OptionValueAPIView.as_view()),
    path("call-value", CallValueAPIView.as_view()),
    path("put-value", PutValueAPIView.as_view()),
    path("call-to-put", CallToPutAPIView.as_view()),
    path("option-to-market", OptionToMarketAPIView.as_view()),
]

domestic_urls = [
    path("domestic-top-price-change", DomesticMeanDeviationAPIView.as_view()),
]

global_urls = [
    path("global-top-price-change", GlobalMeanDeviationAPIView.as_view()),
]

stock_urls = [
    path("industry-roi", IndustryROIAPIView.as_view()),
    path("pe", MinimumPEAPIView.as_view()),
]

urlpatterns = (
    [
        path("buy-sell-value", BuySellValueAPIView.as_view()),
        path("last-close-price", LastClosePriceAPIView.as_view()),
        path("dollar-price", DollarPriceAPIView.as_view()),
    ]
    + dashboard_menu_urls
    + index_urls
    + option_urls
    + domestic_urls
    + global_urls
    + stock_urls
)
