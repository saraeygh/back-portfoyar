from rest_framework.permissions import BasePermission

from account.models import ALL_FEATURE, STOCK_FEATURE

STOCK_PERM_LIST = [ALL_FEATURE, STOCK_FEATURE]


class HasStockSubscription(BasePermission):
    message = "no-stock-sub"

    def has_permission(self, request, view):
        return request.user.subscription.filter(
            feature__name__in=STOCK_PERM_LIST, is_enabled=True
        ).exists()
