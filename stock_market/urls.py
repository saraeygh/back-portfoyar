from django.urls import path
from stock_market.views import (
    StockPersonBuyPressureAPIView,
    StockPersonMoneyFlowAPIView,
    StockPersonBuyValueAPIView,
    StockBuyOrderRatioAPIView,
    StockSellOrderRatioAPIView,
    StockIndustryInstrumentROIAPIView,
    StockIndustryROIAPIView,
    StockOveralROIAPIView,
    StockValueChangeAPIView,
    StockCallValueChangeAPIView,
    StockOptionPriceSpreadAPIView,
    StockRecommendedAPIView,
    StockRecommendationConfigAPIView,
    StockRecommendationConfigSettingAPIView,
    StockRecommendationConfigAPIViewV2,
    StockDashboardAPIView,
    OptionDashboardAPIView,
)

dashboard_urls = [
    path("stock/", StockDashboardAPIView.as_view()),
    path("option/", OptionDashboardAPIView.as_view()),
]

market_watch_behaviour_urls = [
    path("person-money-flow/", StockPersonMoneyFlowAPIView.as_view()),
    path("person-buy-pressure/", StockPersonBuyPressureAPIView.as_view()),
    path("person-buy-value/", StockPersonBuyValueAPIView.as_view()),
    path("buy-order-ratio/", StockBuyOrderRatioAPIView.as_view()),
    path("sell-order-ratio/", StockSellOrderRatioAPIView.as_view()),
]

market_value_urls = [
    path("value-change/", StockValueChangeAPIView.as_view()),
]

market_roi_urls = [
    path("roi/", StockOveralROIAPIView.as_view()),
    path("industry-roi/", StockIndustryROIAPIView.as_view()),
    path("roi/<int:industry_id>", StockIndustryInstrumentROIAPIView.as_view()),
]

option_behavior_urls = [
    path(
        "option-value-change/<str:option_type>", StockCallValueChangeAPIView.as_view()
    ),
    path("option-price-spread/", StockOptionPriceSpreadAPIView.as_view()),
]

stock_recommendation_urls = [
    # V1
    path("recomm-config-new/", StockRecommendationConfigAPIView.as_view()),
    path(
        "recomm-config-new/<int:config_id>/", StockRecommendationConfigAPIView.as_view()
    ),
    path(
        "recomm-config-new/<int:config_id>/<str:setting_name>/",
        StockRecommendationConfigSettingAPIView.as_view(),
    ),
    # V2
    path("v2/recomm-config/", StockRecommendationConfigAPIViewV2.as_view()),
    # Positions
    path("recommended/", StockRecommendedAPIView.as_view()),
]

urlpatterns = (
    dashboard_urls
    + market_watch_behaviour_urls
    + market_roi_urls
    + market_value_urls
    + option_behavior_urls
    + stock_recommendation_urls
)
