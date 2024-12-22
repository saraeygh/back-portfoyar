import datetime as dt

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from account.models import Profile, Subscription, Feature, ALL_FEATURE

NEW_USER_FREE_FEATURES = [ALL_FEATURE]

NEW_USER_FREE_DURATION = 7


@receiver(post_save, sender=User)
def create_profile(sender, instance: User, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_free_subscription(sender, instance: User, created, **kwargs):
    if created:
        for free_feature in NEW_USER_FREE_FEATURES:
            free_feature = (
                Feature.objects.filter(is_enabled=True, name=free_feature)
                .order_by("duration")
                .first()
            )
            if free_feature:
                start_at = dt.datetime.now().date()
                end_at = start_at + dt.timedelta(days=NEW_USER_FREE_DURATION)

                Subscription.objects.create(
                    user=instance,
                    feature=free_feature,
                    start_at=start_at,
                    end_at=end_at,
                )
