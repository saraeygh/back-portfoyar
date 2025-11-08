from datetime import datetime as dt, timedelta as td

from django.contrib.auth.models import User

from core.models import FeatureToggle
from core.utils import NEW_USER_FREE_DURATION


from account.models import FirstLogin, Subscription, Feature, ALL_FEATURE, ONE_MONTH

NEW_USER_FREE_FEATURES = [ALL_FEATURE]


def new_user_subscription(user: User, first_login: FirstLogin):
    if not first_login.has_logged_in:
        for free_feature in NEW_USER_FREE_FEATURES:
            free_feature = (
                Feature.objects.filter(is_enabled=True, name=free_feature)
                .order_by("duration")
                .first()
            )

            if free_feature is None:
                free_feature = Feature.objects.create(
                    name=free_feature, duration=ONE_MONTH, price=0
                )

            start_at = dt.now().date()

            free_sub = FeatureToggle.objects.filter(
                name=NEW_USER_FREE_DURATION["name"]
            ).first()
            end_at = start_at + td(days=int(free_sub.value))

            Subscription.objects.create(
                user=user,
                feature=free_feature,
                start_at=start_at,
                end_at=end_at,
            )

        first_login.has_logged_in = True
        first_login.save()


def apply_kish_expo_gift(user: User, first_login: FirstLogin):

    if user.username.startswith("kish"):

        if not first_login.has_logged_in:
            feature = (
                Feature.objects.filter(is_enabled=True, name=ALL_FEATURE)
                .order_by("duration")
                .first()
            )

            if feature is None:
                feature = Feature.objects.create(
                    name=ALL_FEATURE, duration=ONE_MONTH, price=0
                )

            Subscription.objects.create(
                user=user,
                feature=feature,
                start_at=dt.now().date(),
                end_at=(dt.now() + td(days=30)).date(),
                desc="1404-kish-expo-gift",
            )

            first_login.has_logged_in = True
            first_login.save()
