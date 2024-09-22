from django.core.management.base import BaseCommand
from core.utils import (
    create_admin_user,
    create_default_recommendation_setting,
    create_default_feature_toggle,
    populate_strategy_option,
    populate_option_strategy,
    populate_option_strategy_old,
)


class Command(BaseCommand):
    help = "Create strategies"

    def handle(self, *args, **options):

        create_admin_user()

        create_default_recommendation_setting()

        create_default_feature_toggle()

        populate_strategy_option()
        # OLD
        populate_option_strategy()
        populate_option_strategy_old()
