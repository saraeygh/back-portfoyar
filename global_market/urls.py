from django.urls import path
from global_market.views import (
    GetCommodityListAPIView,
    GetCommodityTypeListAPIView,
    GetIndustryListAPIView,
    GetTransitListAPIView,
    GlobalPriceChartAPIView,
    GlobalRatioChartAPIView,
    MeanDeviationAPIView,
    MeanDeviationAPIViewV2,
    RelatedStockAPIView,
    UploadXLSXDataAPIView,
    UploadRelationAPIView,
)

upload_data_urls = [
    path("upload-data", UploadXLSXDataAPIView.as_view()),
    path("upload-relation", UploadRelationAPIView.as_view()),
]

industry_urls = [
    path("industry", GetIndustryListAPIView.as_view()),
]

commodity_type_urls = [
    path("commodity-type/<int:industry_id>", GetCommodityTypeListAPIView.as_view()),
]

commodity_urls = [
    path("commodity/<int:commodity_type_id>", GetCommodityListAPIView.as_view()),
]

transit_urls = [
    path("transit/<int:commodity_id>", GetTransitListAPIView.as_view()),
]

chart_urls = [
    path("price-chart", GlobalPriceChartAPIView.as_view()),
    path("ratio-chart", GlobalRatioChartAPIView.as_view()),
]

strategy_urls = [
    path("mean-deviation", MeanDeviationAPIView.as_view()),
    # MEAN-DEVIATION NEW VERSION
    path("top-price-change", MeanDeviationAPIViewV2.as_view()),
    path("related-stock", RelatedStockAPIView.as_view()),
]

urlpatterns = (
    industry_urls
    + upload_data_urls
    + commodity_type_urls
    + chart_urls
    + commodity_urls
    + transit_urls
    + strategy_urls
)
