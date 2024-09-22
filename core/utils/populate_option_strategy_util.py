from option_market.models import OptionStrategy, RiskLevel


PROFIT_STATUS = {
    "covered_call": "limited_profit",
    "long_call": "unlimited_profit",  # unlimited_profit
    "short_call": "limited_profit",
    "long_put": "limited_profit",
    "short_put": "limited_profit",
    "long_straddle": "unlimited_profit",  # unlimited_profit
    "short_straddle": "limited_profit",
    "bull_call_spread": "limited_profit",
    "bear_call_spread": "limited_profit",
    "bull_put_spread": "limited_profit",
    "bear_put_spread": "limited_profit",
    "long_strangle": "unlimited_profit",  # unlimited_profit
    "short_strangle": "limited_profit",
    "long_butterfly": "limited_profit",
    "short_butterfly": "limited_profit",
    "collar": "unlimited_profit",  # unlimited_profit
}


def create_or_update(strategy_dict: dict, risk_level: str):
    for key, name in strategy_dict.items():
        try:
            strategy = OptionStrategy.objects.get(key=key)
            strategy.name = name
            strategy.save()
        except OptionStrategy.DoesNotExist:
            strategy = OptionStrategy.objects.create(name=name, key=key)

        if RiskLevel.objects.filter(
            option_strategy=strategy,
            profit_status=PROFIT_STATUS.get(strategy.key),
            level=risk_level,
        ).exists():
            continue
        RiskLevel.objects.create(
            option_strategy=strategy,
            profit_status=PROFIT_STATUS.get(strategy.key),
            level=risk_level,
        )


def populate_option_strategy():
    print("Creating pre-defined strategies ...")

    NO_RISKS = {}

    LOW_RISKS = {
        "covered_call": "کاورد کال",
        "bull_call_spread": "بول کال اسپرد",
        "bull_put_spread": "بول پوت اسپرد",
        "short_put": "شورت پوت",
        "short_call": "شورت کال",
    }
    HIGH_RISKS = {
        "covered_call": "کاورد کال",
        "bull_call_spread": "بول کال اسپرد",
        "short_strangle": "شورت استرانگل",
        "bear_put_spread": "بیر پوت اسپرد",
        "bear_call_spread": "بیر کال اسپرد",
        "short_straddle": "شورت استردل",
        "short_butterfly": "شورت باترفلای",
        "short_put": "شورت پوت",
        "short_call": "شورت کال",
        "long_butterfly": "لانگ باترفلای",
        "long_put": "لانگ پوت",
    }

    LOWER_RISKS = {
        "long_strangle": "لانگ استرانگل",
        "collar": "کولار",
    }

    HIGHER_RISK_ROIS = {
        "long_strangle": "لانگ استرانگل",
        "long_straddle": "لانگ استردل",
        "long_call": "لانگ کال",
        "collar": "کولار",
    }

    create_or_update(strategy_dict=NO_RISKS, risk_level="no_risk")
    create_or_update(strategy_dict=LOW_RISKS, risk_level="low_risk")
    create_or_update(strategy_dict=HIGH_RISKS, risk_level="high_risk")
    create_or_update(strategy_dict=LOWER_RISKS, risk_level="lower_risk")
    create_or_update(strategy_dict=HIGHER_RISK_ROIS, risk_level="higher_risk_roi")

    print("Created strategies.")
