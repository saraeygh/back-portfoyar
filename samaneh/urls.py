from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

from samaneh.settings.common import DEBUG, STATIC_ROOT

if DEBUG:
    from .test_view import TestView

    test_urls = [
        path("api/test/", TestView.as_view()),
    ]
else:
    test_urls = []

urlpatterns = [
    path("api/admin/", admin.site.urls),
    path("api/account/", include("account.urls")),
    path("api/support/", include("support.urls")),
    # APP'S URLS
    path("api/domestic/", include("domestic_market.urls")),
    path("api/favorite/", include("favorite.urls")),
    path("api/global-market/", include("global_market.urls")),
    path("api/option/", include("option_market.urls")),
    path("api/stock-market/", include("stock_market.urls")),
    # STATIC FILES SERVING URL
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": STATIC_ROOT}),
] + test_urls
