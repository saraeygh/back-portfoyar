from django.urls import path

from dashboard.views import (
    BuySellValueAPIView,
    IndustrialGroupsAPIView,
    PaperTypesAPIView,
)

dashboard_menu_urls = [
    path("industrial-groups/", IndustrialGroupsAPIView.as_view()),
    path("paper-types/", PaperTypesAPIView.as_view()),
]


urlpatterns = [
    path("buy-sell-value/", BuySellValueAPIView.as_view()),
] + dashboard_menu_urls
