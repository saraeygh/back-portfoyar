from rest_framework.permissions import BasePermission

from account.models import ALL_FEATURE, GLOBAL_FEATURE

GLOBAL_PERM_LIST = [ALL_FEATURE, GLOBAL_FEATURE]


class HasGlobalSubscription(BasePermission):
    message = "no-global-sub"

    def has_permission(self, request, view):
        return request.user.subscription.filter(
            feature__name__in=GLOBAL_PERM_LIST, is_enabled=True
        ).exists()
