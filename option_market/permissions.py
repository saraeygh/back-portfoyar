from rest_framework.permissions import BasePermission

from account.models import ALL_FEATURE, OPTION_FEATURE

OPTION_PERM_LIST = [ALL_FEATURE, OPTION_FEATURE]


class HasOptionSubscription(BasePermission):
    message = "no-option-sub"

    def has_permission(self, request, view):
        return request.user.subscription.filter(
            feature__name__in=OPTION_PERM_LIST, is_enabled=True
        ).exists()
