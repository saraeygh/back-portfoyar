from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

from samaneh.settings.common import DEBUG, STATIC_ROOT

test_urls = []
if DEBUG:
    from .test_view import TestView

    test_urls = [
        path("api/test/", TestView.as_view()),
    ]

urlpatterns = [
    path("api/admin/", admin.site.urls),
    # APP'S URLS
    path("api/account/", include("account.urls")),
    path("api/dashboard/", include("dashboard.urls")),
    path("api/domestic/", include("domestic_market.urls")),
    path("api/favorite/", include("favorite.urls")),
    path("api/future/", include("future_market.urls")),
    path("api/global-market/", include("global_market.urls")),
    path("api/option/", include("option_market.urls")),
    path("api/payment/", include("payment.urls")),
    path("api/stock-market/", include("stock_market.urls")),
    path("api/support/", include("support.urls")),
    path("", include("django_prometheus.urls")),
    # STATIC FILES SERVING URL
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": STATIC_ROOT}),
] + test_urls
