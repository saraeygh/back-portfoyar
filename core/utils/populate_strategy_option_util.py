from option_market.models import StrategyOption

STRATEGIES = {
    "covered_call": {
        "name": "کاورد کال",
        "profit_status": "limited_profit",
        "risk_levels": ["low_risk", "high_risk"],
    },
    "long_call": {
        "name": "لانگ کال",
        "profit_status": "unlimited_profit",
        "risk_levels": ["high_risk"],
    },
    "short_call": {
        "name": "شورت کال",
        "profit_status": "limited_profit",
        "risk_levels": ["high_risk"],
    },
    "long_put": {
        "name": "لانگ پوت",
        "profit_status": "unlimited_profit",
        "risk_levels": ["high_risk"],
    },
    "short_put": {
        "name": "شورت پوت",
        "profit_status": "limited_profit",
        "risk_levels": ["low_risk", "high_risk"],
    },
    "long_straddle": {
        "name": "لانگ استرادل",
        "profit_status": "unlimited_profit",
        "risk_levels": ["high_risk"],
    },
    "short_straddle": {
        "name": "شورت استرادل",
        "profit_status": "limited_profit",
        "risk_levels": ["high_risk"],
    },
    "bull_call_spread": {
        "name": "بول کال اسپرد",
        "profit_status": "limited_profit",
        "risk_levels": ["low_risk", "high_risk"],
    },
    "bear_call_spread": {
        "name": "بیر کال اسپرد",
        "profit_status": "limited_profit",
        "risk_levels": ["high_risk"],
    },
    "bull_put_spread": {
        "name": "بول پوت اسپرد",
        "profit_status": "limited_profit",
        "risk_levels": ["low_risk", "high_risk"],
    },
    "bear_put_spread": {
        "name": "بیر پوت اسپرد",
        "profit_status": "limited_profit",
        "risk_levels": ["low_risk", "high_risk"],
    },
    "long_strangle": {
        "name": "لانگ استرانگل",
        "profit_status": "unlimited_profit",
        "risk_levels": ["low_risk", "high_risk"],
    },
    "short_strangle": {
        "name": "شورت استرانگل",
        "profit_status": "limited_profit",
        "risk_levels": ["high_risk"],
    },
    "long_butterfly": {
        "name": "لانگ باترفلای",
        "profit_status": "limited_profit",
        "risk_levels": ["high_risk"],
    },
    "short_butterfly": {
        "name": "شورت باترفلای",
        "profit_status": "limited_profit",
        "risk_levels": ["high_risk"],
    },
    "collar": {
        "name": "کولار",
        "profit_status": "unlimited_profit",
        "risk_levels": ["low_risk", "high_risk"],
    },
    "conversion": {
        "name": "کانورژن",
        "profit_status": "limited_profit",
        "risk_levels": ["no_risk"],
    },
}


def create_or_update(strategy_key: str, profit_status: str, risk_level: str, name: str):
    try:
        strategy = StrategyOption.objects.get(
            key=strategy_key, profit_status=profit_status, risk_level=risk_level
        )
        strategy.name = name
        strategy.save()
    except StrategyOption.DoesNotExist:
        strategy = StrategyOption.objects.create(
            name=name,
            key=strategy_key,
            profit_status=profit_status,
            risk_level=risk_level,
        )


def populate_strategy_option():
    print("Creating pre-defined strategies ...")

    for strategy_key, strategy_properties in STRATEGIES.items():
        name = strategy_properties.get("name")
        profit_status = strategy_properties.get("profit_status")
        risk_levels = strategy_properties.get("risk_levels")
        for risk_level in risk_levels:
            create_or_update(strategy_key, profit_status, risk_level, name)

    print("Created strategies.")
