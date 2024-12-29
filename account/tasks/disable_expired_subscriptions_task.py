from datetime import datetime as dt

from core.utils import run_main_task
from account.models import Subscription


def disable_expired_subscription_main():
    current_date = dt.now().date()
    expired_subs = Subscription.objects.filter(is_enabled=True, end_at__lt=current_date)
    expired_subs.update(is_enabled=False)


def disable_expired_subscription():

    run_main_task(
        main_task=disable_expired_subscription_main,
        daily=True,
    )
