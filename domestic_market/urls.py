from django.urls import path
from domestic_market.views import (
    DomesticPriceChartAPIView,
    DomesticPriceChartByProducerAPIView,
    DomesticRatioChartAPIView,
    DomesticRatioChartByProducerAPIView,
    GetCommodityListAPIView,
    GetCommodityListByProducerAPIView,
    GetCommodityTypeListAPIView,
    GetDollarPriceAPIView,
    GetIndustryListAPIView,
    GetProducerListByCommodityAPIView,
    GetProducerListAPIView,
    MeanDeviationAPIView,
    MeanDeviationAPIViewV2,
    UploadDollarPriceAPIView,
    ProducerSellReportAPIView,
    ProducerSellReportAPIViewV2,
    GetCommodityNameListByProducerAPIView,
    UploadRelationAPIView,
)

# BY PRODUCER URLs
by_producer_urls = [
    path("producer/company", GetProducerListAPIView.as_view()),
    path(
        "producer/group/<int:company_id>",
        GetCommodityListByProducerAPIView.as_view(),
    ),
    path(
        "producer/commodity/<int:company_id>/<int:group_id>",
        GetCommodityNameListByProducerAPIView.as_view(),
    ),
    path("producer/price-chart", DomesticPriceChartByProducerAPIView.as_view()),
    path("producer/ratio-chart", DomesticRatioChartByProducerAPIView.as_view()),
]

# BY CATEGORY URLs
by_category_urls = [
    path("category/industry", GetIndustryListAPIView.as_view()),
    path("category/field/<int:industry_id>", GetCommodityTypeListAPIView.as_view()),
    path("category/group/<int:field_id>", GetCommodityListAPIView.as_view()),
    path(
        "category/company/<int:group_id>",
        GetProducerListByCommodityAPIView.as_view(),
    ),
    path(
        "category/commodity/<int:company_id>/<int:group_id>",
        GetCommodityNameListByProducerAPIView.as_view(),
    ),
    path("category/price-chart", DomesticPriceChartAPIView.as_view()),
    path("category/ratio-chart", DomesticRatioChartAPIView.as_view()),
]


# STRATEGIES
strategy_urls = [
    path("mean-deviation", MeanDeviationAPIView.as_view()),
    # MEAN-DEVIATION NEW VERSION
    path("top-price-change", MeanDeviationAPIViewV2.as_view()),
]

# REPORTS
report_urls = [
    path("producer-sell/<int:company_id>", ProducerSellReportAPIView.as_view()),
    path("producer-sell", ProducerSellReportAPIViewV2.as_view()),
]

# DOLLAR
dollar_urls = [
    path("upload-dollar", UploadDollarPriceAPIView.as_view()),
    path("dollar", GetDollarPriceAPIView.as_view()),
]

relation_urls = [
    path("upload-relation", UploadRelationAPIView.as_view()),
]

urlpatterns = (
    by_producer_urls
    + by_category_urls
    + strategy_urls
    + report_urls
    + dollar_urls
    + relation_urls
)
