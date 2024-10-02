from django.core.management.base import BaseCommand
from core.utils import (
    create_admin_user,
    create_default_recommendation_setting,
    create_default_feature_toggle,
    populate_strategy_option,
    create_profile_for_users_with_no_profile,
)


class Command(BaseCommand):
    help = "Create strategies"

    def handle(self, *args, **options):

        create_admin_user()

        create_default_recommendation_setting()

        create_default_feature_toggle()

        populate_strategy_option()

        create_profile_for_users_with_no_profile()
