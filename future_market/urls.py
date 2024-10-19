from django.urls import path

from future_market.views import MonthlyInterestRateAPIView, FuturePositionsAPIView

future_urls = [
    path("monthly-interest-rate/", MonthlyInterestRateAPIView.as_view()),
    path("positions/", FuturePositionsAPIView.as_view()),
]

urlpatterns = future_urls
