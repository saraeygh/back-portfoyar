import time
import datetime as dt

from django.db.models import F
from django.contrib.auth.models import User

from colorama import Fore, Style

from account.models import Feature, Subscription, SUBSCRIPTION_FEATURE_CHOICES

FEATURES = {feature[0]: feature[1] for feature in SUBSCRIPTION_FEATURE_CHOICES}


def create_sub_for_all_no_sub_users():
    users_with_sub = list(
        Subscription.objects.filter(is_enabled=True).values_list("user", flat=True)
    )
    print(f"There are - {len(users_with_sub)} - users with active sub")

    users_without_sub = User.objects.exclude(id__in=users_with_sub)
    print(f"There are - {users_without_sub.count()} - users without sub")

    active_features = Feature.objects.filter(is_enabled=True)

    try:
        for feat in active_features:
            print(
                f"ID: {feat.id}, {feat.name}, {feat.duration} month(s),"
                f" {feat.price} Toman ({feat.discounted_price}), {feat.login_count} users"
            )

        feature_id = int(input("Choose feature ID: "))
        selected_feature = Feature.objects.get(id=feature_id)

        duration = int(input("Subscription duration in days: "))

        start_at = dt.datetime.now().date()
        end_at = start_at + dt.timedelta(days=duration)

        new_subs = []
        for user in users_without_sub:
            new_sub = {
                "user": user,
                "feature": selected_feature,
                "start_at": start_at,
                "end_at": end_at,
                "desc": "manually-created",
            }

            new_sub = Subscription(**new_sub)
            new_subs.append(new_sub)

        if new_subs:
            Subscription.objects.bulk_create(new_subs)

        print(f"Created - {len(new_subs)} - subs")

    except Exception:
        print(Fore.RED + "Something happend! Try again..." + Style.RESET_ALL)
        time.sleep(0.5)


def add_days_to_subs():

    try:
        is_enabled = {"1": [True], "2": [False], "3": [True, False]}
        print(
            "1) Just active subs",
            "2) Just not-active subs",
            "3) Active or not-active subs",
            sep="\n",
        )
        sub_type = is_enabled.get(input("Choose sub type: "), [])

        selected_subs = Subscription.objects.filter(is_enabled__in=sub_type)
        print(f"Sub's is_enabled = {sub_type}, count: {selected_subs.count()}")

        days_to_add = int(input("number of days: "))

        now_date = dt.datetime.now().date()
        disabled_subs = selected_subs.filter(is_enabled=False)
        disabled_subs.update(end_at=now_date)

        selected_subs.update(
            is_enabled=True, end_at=F("end_at") + dt.timedelta(days=days_to_add)
        )

    except Exception:
        print(Fore.RED + "Something happend! Try again..." + Style.RESET_ALL)
        time.sleep(0.5)
