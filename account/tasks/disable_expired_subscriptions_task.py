from datetime import datetime as dt

from account.models import Subscription


def disable_expired_subscription():
    current_date = dt.now().date()
    expired_subs = Subscription.objects.filter(is_enabled=True, end_at__lt=current_date)
    expired_subs.update(is_enabled=False)
