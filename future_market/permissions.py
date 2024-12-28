from rest_framework.permissions import BasePermission

from account.models import ALL_FEATURE, FUTURE_FEATURE

FUTURE_PERM_LIST = [ALL_FEATURE, FUTURE_FEATURE]


class HasFutureSubscription(BasePermission):
    message = "no-future-sub"

    def has_permission(self, request, view):
        return request.user.subscription.filter(
            feature__name__in=FUTURE_PERM_LIST, is_enabled=True
        ).exists()
