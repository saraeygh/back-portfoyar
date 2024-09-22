from core.configs import DEFAULT_RECOMMENDATION_CONFIG_NAME
from stock_market.models import RecommendationConfig
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


def get_recommendation_config(user):

    config = user.configs
    if config.count() < 1:
        config = RecommendationConfig.objects.filter(
            name=DEFAULT_RECOMMENDATION_CONFIG_NAME
        )

        if not config.exists():
            new_config = RecommendationConfig.objects.create(
                user=user, name="پیش‌فرض", is_default=True
            )
            MoneyFlow.objects.create(recommendation=new_config, is_enabled=True)
            BuyPressure.objects.create(recommendation=new_config, is_enabled=True)
            BuyValue.objects.create(recommendation=new_config, is_enabled=True)
            BuyRatio.objects.create(recommendation=new_config, is_enabled=True)
            SellRatio.objects.create(recommendation=new_config, is_enabled=True)
            ROI.objects.create(recommendation=new_config, is_enabled=True)
            ValueChange.objects.create(recommendation=new_config, is_enabled=True)
            CallValueChange.objects.create(recommendation=new_config, is_enabled=True)
            PutValueChange.objects.create(recommendation=new_config, is_enabled=True)
            OptionPriceSpread.objects.create(recommendation=new_config, is_enabled=True)
            GlobalPositiveRange.objects.create(
                recommendation=new_config, is_enabled=True
            )
            GlobalNegativeRange.objects.create(
                recommendation=new_config, is_enabled=True
            )
            DomesticPositiveRange.objects.create(
                recommendation=new_config, is_enabled=True
            )
            DomesticNegativeRange.objects.create(
                recommendation=new_config, is_enabled=True
            )

            config = new_config

    elif config.count() > 1:
        default_configs = config.filter(is_default=True)
        if default_configs.count() < 1:
            config = config.first()
        elif default_configs.count() > 1:
            config = default_configs.first()
        else:
            config = default_configs.first()

    if not isinstance(config, RecommendationConfig):
        config = config.first()

    return config
