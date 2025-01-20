from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("api/admin/", admin.site.urls),
    path("api/core/", include("core.urls")),
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
]
