from django.urls import path

from payment.views import ZarinpalPaymentAPIView

zarinpal_urls = [
    path("zarinpal/<str:receipt_id>", ZarinpalPaymentAPIView.as_view()),
]


urlpatterns = zarinpal_urls
