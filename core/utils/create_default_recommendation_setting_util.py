from django.contrib.auth.models import User
from stock_market.models import RecommendationConfig
from .create_admin_user_util import ADMIN_USERNAME
from stock_market.models.recommendation_config_model import (
    MoneyFlow,
    BuyPressure,
    BuyValue,
    BuyRatio,
    SellRatio,
    ROI,
    ValueChange,
    CallValueChange,
    PutValueChange,
    OptionPriceSpread,
    GlobalPositiveRange,
    GlobalNegativeRange,
    DomesticPositiveRange,
    DomesticNegativeRange,
)
from colorama import Fore, Style

DEFAULT_SETTING_NAME = "portfoyar_admin_default_recommendation_configs"


def create_default_recommendation_setting():
    try:

        default_setting = RecommendationConfig.objects.get(name=DEFAULT_SETTING_NAME)
        if not default_setting.is_default:
            default_setting.is_default = True
            default_setting.save()

        print(Fore.YELLOW + "Default settings already exists." + Style.RESET_ALL)
    except RecommendationConfig.DoesNotExist:
        admin_user = User.objects.get(username=ADMIN_USERNAME)

        default_setting: RecommendationConfig = RecommendationConfig.objects.create(
            user=admin_user, name=DEFAULT_SETTING_NAME, is_default=True
        )
        MoneyFlow.objects.create(recommendation=default_setting, is_enabled=True)
        BuyPressure.objects.create(recommendation=default_setting, is_enabled=True)
        BuyValue.objects.create(recommendation=default_setting, is_enabled=True)
        BuyRatio.objects.create(recommendation=default_setting, is_enabled=True)
        SellRatio.objects.create(recommendation=default_setting, is_enabled=True)
        ROI.objects.create(recommendation=default_setting, is_enabled=True)
        ValueChange.objects.create(recommendation=default_setting, is_enabled=True)
        CallValueChange.objects.create(recommendation=default_setting, is_enabled=True)
        PutValueChange.objects.create(recommendation=default_setting, is_enabled=True)
        OptionPriceSpread.objects.create(
            recommendation=default_setting, is_enabled=True
        )
        GlobalPositiveRange.objects.create(
            recommendation=default_setting, is_enabled=True
        )
        GlobalNegativeRange.objects.create(
            recommendation=default_setting, is_enabled=True
        )
        DomesticPositiveRange.objects.create(
            recommendation=default_setting, is_enabled=True
        )
        DomesticNegativeRange.objects.create(
            recommendation=default_setting, is_enabled=True
        )

        print(Fore.GREEN + "Default settings created." + Style.RESET_ALL)
