from django.urls import path

from future_market.views import FuturePositionsAPIView

future_urls = [
    path("positions/", FuturePositionsAPIView.as_view()),
]

urlpatterns = future_urls
