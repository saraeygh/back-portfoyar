from rest_framework.permissions import BasePermission

from account.models import ALL_FEATURE, DOMESTIC_FEATURE

DOMESTIC_PERM_LIST = [ALL_FEATURE, DOMESTIC_FEATURE]


class HasDomesticSubscription(BasePermission):
    message = "no-domestic-sub"

    def has_permission(self, request, view):
        return request.user.subscription.filter(
            feature__name__in=DOMESTIC_PERM_LIST, is_enabled=True
        ).exists()
