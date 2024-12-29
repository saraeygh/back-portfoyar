from datetime import datetime as dt

from core.utils import send_task_fail_success_email, print_task_info
from account.models import Subscription


def disable_expired_subscription_main():
    current_date = dt.now().date()
    expired_subs = Subscription.objects.filter(is_enabled=True, end_at__lt=current_date)
    expired_subs.update(is_enabled=False)


def disable_expired_subscription():
    TASK_NAME = disable_expired_subscription.__name__
    print_task_info(name=TASK_NAME)

    try:
        disable_expired_subscription_main()
        send_task_fail_success_email(task_name=TASK_NAME)
    except Exception as e:
        send_task_fail_success_email(task_name=TASK_NAME, exception=e)

    print_task_info(color="GREEN", name=TASK_NAME)
