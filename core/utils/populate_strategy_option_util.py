from option_market.models import StrategyOption
from colorama import Fore, Style

COVERED_CALL_SEQ = 1
CONVERSION_SEQ = 2
LONG_CALL_SEQ = 3
SHORT_CALL_DEQ = 4
LONG_PUT_SEQ = 5
SHORT_PUT_SEQ = 6
LONG_STRADDLE_SEQ = 7
SHORT_STRADDLE_SEQ = 8
BULL_CALL_SPREAD_SEQ = 9
BEAR_CALL_SPREAD_SEQ = 10
BULL_PUT_SPREAD_SEQ = 11
BEAR_PUT_SPREAD_SEQ = 12
LONG_STRANGLE_SEQ = 13
SHORT_STRANGLE_SEQ = 14
LONG_BUTTERFLY_SEQ = 15
SHORT_BUTTERFLY_SEQ = 16
COLLAR_SEQ = 17

STRATEGIES = {
    "covered_call": {
        "name": "کاورد کال",
        "profit_status": "limited_profit",
        "risk_levels": ["low_risk", "high_risk"],
        "sequence": COVERED_CALL_SEQ,
    },
    "long_call": {
        "name": "لانگ کال",
        "profit_status": "unlimited_profit",
        "risk_levels": ["high_risk"],
        "sequence": LONG_CALL_SEQ,
    },
    "short_call": {
        "name": "شورت کال",
        "profit_status": "limited_profit",
        "risk_levels": ["high_risk"],
        "sequence": SHORT_CALL_DEQ,
    },
    "long_put": {
        "name": "لانگ پوت",
        "profit_status": "unlimited_profit",
        "risk_levels": ["high_risk"],
        "sequence": LONG_PUT_SEQ,
    },
    "short_put": {
        "name": "شورت پوت",
        "profit_status": "limited_profit",
        "risk_levels": ["low_risk", "high_risk"],
        "sequence": SHORT_PUT_SEQ,
    },
    "long_straddle": {
        "name": "لانگ استرادل",
        "profit_status": "unlimited_profit",
        "risk_levels": ["high_risk"],
        "sequence": LONG_STRADDLE_SEQ,
    },
    "short_straddle": {
        "name": "شورت استرادل",
        "profit_status": "limited_profit",
        "risk_levels": ["high_risk"],
        "sequence": SHORT_STRADDLE_SEQ,
    },
    "bull_call_spread": {
        "name": "بول کال اسپرد",
        "profit_status": "limited_profit",
        "risk_levels": ["low_risk", "high_risk"],
        "sequence": BULL_CALL_SPREAD_SEQ,
    },
    "bear_call_spread": {
        "name": "بیر کال اسپرد",
        "profit_status": "limited_profit",
        "risk_levels": ["high_risk"],
        "sequence": BEAR_CALL_SPREAD_SEQ,
    },
    "bull_put_spread": {
        "name": "بول پوت اسپرد",
        "profit_status": "limited_profit",
        "risk_levels": ["low_risk", "high_risk"],
        "sequence": BULL_PUT_SPREAD_SEQ,
    },
    "bear_put_spread": {
        "name": "بیر پوت اسپرد",
        "profit_status": "limited_profit",
        "risk_levels": ["low_risk", "high_risk"],
        "sequence": BEAR_PUT_SPREAD_SEQ,
    },
    "long_strangle": {
        "name": "لانگ استرانگل",
        "profit_status": "unlimited_profit",
        "risk_levels": ["low_risk", "high_risk"],
        "sequence": LONG_STRANGLE_SEQ,
    },
    "short_strangle": {
        "name": "شورت استرانگل",
        "profit_status": "limited_profit",
        "risk_levels": ["high_risk"],
        "sequence": SHORT_STRANGLE_SEQ,
    },
    "long_butterfly": {
        "name": "لانگ باترفلای",
        "profit_status": "limited_profit",
        "risk_levels": ["high_risk"],
        "sequence": LONG_BUTTERFLY_SEQ,
    },
    "short_butterfly": {
        "name": "شورت باترفلای",
        "profit_status": "limited_profit",
        "risk_levels": ["high_risk"],
        "sequence": SHORT_BUTTERFLY_SEQ,
    },
    "collar": {
        "name": "کولار",
        "profit_status": "unlimited_profit",
        "risk_levels": ["low_risk", "high_risk"],
        "sequence": COLLAR_SEQ,
    },
    "conversion": {
        "name": "کانورژن",
        "profit_status": "limited_profit",
        "risk_levels": ["no_risk"],
        "sequence": CONVERSION_SEQ,
    },
}


def create_or_update(
    strategy_key: str, profit_status: str, risk_level: str, name: str, sequence: int
):
    try:
        strategy = StrategyOption.objects.get(
            key=strategy_key, profit_status=profit_status, risk_level=risk_level
        )
        strategy.name = name
        strategy.sequence = sequence
        strategy.save()
    except StrategyOption.DoesNotExist:
        strategy = StrategyOption.objects.create(
            name=name,
            key=strategy_key,
            profit_status=profit_status,
            risk_level=risk_level,
            sequence=sequence,
        )


def populate_strategy_option():
    print(Fore.BLUE + "Creating pre-defined strategies ..." + Style.RESET_ALL)
    for strategy_key, strategy_properties in STRATEGIES.items():
        name = strategy_properties.get("name")
        profit_status = strategy_properties.get("profit_status")
        risk_levels = strategy_properties.get("risk_levels")
        sequence = strategy_properties.get("sequence")
        for risk_level in risk_levels:
            create_or_update(strategy_key, profit_status, risk_level, name, sequence)

    print(Fore.GREEN + "Created strategies." + Style.RESET_ALL)
