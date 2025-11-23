from option_market.models import StrategyOption


COVERED_CALL_SEQ = 1
COVERED_CALL_DESC = "خرید سهم و فروش کال"

CONVERSION_SEQ = 2
CONVERSION_DESC = "خرید سهم و فروش کال و خرید پوت با قیمت اعمال یکسان"

MARRIED_PUT_SEQ = 3
MARRIED_PUT_DESC = "خرید سهم و خرید پوت با قیمت اعمال کمتر از قیمت سهم"

LONG_CALL_SEQ = 4
LONG_CALL_DESC = "خرید کال"

SHORT_CALL_SEQ = 5
SHORT_CALL_DESC = "فروش کال"

LONG_PUT_SEQ = 6
LONG_PUT_DESC = "خرید پوت"

SHORT_PUT_SEQ = 7
SHORT_PUT_DESC = "فروش پوت"

LONG_STRADDLE_SEQ = 8
LONG_STRADDLE_DESC = "خرید همزمان کال و پوت با قیمت اعمال یکسان"

SHORT_STRADDLE_SEQ = 9
SHORT_STRADDLE_DESC = "فروش همزمان کال و پوت با قیمت اعمال یکسان"

BULL_CALL_SPREAD_SEQ = 10
BULL_CALL_SPREAD_DESC = "خرید کال با قیمت اعمال پایین‌تر و فروش کال با قیمت اعمال بالاتر"

BEAR_CALL_SPREAD_SEQ = 11
BEAR_CALL_SPREAD_DESC = "خرید کال با قیمت اعمال بالاتر و فروش کال با قیمت اعمال پایین‌تر"

BULL_PUT_SPREAD_SEQ = 12
BULL_PUT_SPREAD_DESC = "خرید پوت با قیمت اعمال پایین‌تر و فروش پوت با قیمت اعمال بالاتر"

BEAR_PUT_SPREAD_SEQ = 13
BEAR_PUT_SPREAD_DESC = "خرید پوت با قیمت اعمال بالاتر و فروش پوت با قیمت اعمال پایین‌تر"

LONG_STRANGLE_SEQ = 14
LONG_STRANGLE_DESC = "خرید پوت با قیمت اعمال پایین‌تر و خرید کال با قیمت اعمال بالاتر"

SHORT_STRANGLE_SEQ = 15
SHORT_STRANGLE_DESC = "فروش پوت با قیمت اعمال پایین‌تر و فروش کال با قیمت اعمال بالاتر"

LONG_BUTTERFLY_SEQ = 16
LONG_BUTTERFLY_DESC = "خرید کال با قیمت اعمال پایین‌ و دو بار فروش کال با قیمت اعمال میانه و خرید کال با قیمت اعمال بالا"

SHORT_BUTTERFLY_SEQ = 17
SHORT_BUTTERFLY_DESC = "فروش کال با قیمت اعمال پایین‌ و دو بار خرید کال با قیمت اعمال میانه و فروش کال با قیمت اعمال بالا"

COLLAR_SEQ = 18
COLLAR_DESC = (
    "خرید سهم و خرید پوت با قیمت اعمال پایین‌تر و فروش کال با قیمت اعمال بالاتر"
)

STRATEGIES = {
    "covered_call": {
        "name": "کاورد کال",
        "profit_status": "limited_profit",
        "risk_levels": ["low_risk", "high_risk"],
        "sequence": COVERED_CALL_SEQ,
        "desc": COVERED_CALL_DESC,
        "drop_cols": [
            "base_equity_best_sell_price",
            "call_value",
            "required_change",
            "end_date",
            "yearly_profit",
        ],
    },
    "conversion": {
        "name": "کانورژن",
        "profit_status": "limited_profit",
        "risk_levels": ["no_risk"],
        "sequence": CONVERSION_SEQ,
        "desc": CONVERSION_DESC,
        "drop_cols": [
            "base_equity_best_sell_price",
            "call_value",
            "put_value",
            "final_profit",
            "required_change",
            "end_date",
            "yearly_profit",
        ],
    },
    "married_put": {
        "name": "مرید پوت",
        "profit_status": "unlimited_profit",
        "risk_levels": ["low_risk"],
        "sequence": MARRIED_PUT_SEQ,
        "desc": MARRIED_PUT_DESC,
        "drop_cols": [
            "base_equity_best_sell_price",
            "put_value",
            "final_break_even",
            "end_date",
            "yearly_break_even",
        ],
    },
    #
    #
    "long_call": {
        "name": "لانگ کال",
        "profit_status": "unlimited_profit",
        "risk_levels": ["high_risk"],
        "sequence": LONG_CALL_SEQ,
        "desc": LONG_CALL_DESC,
        "drop_cols": ["end_date", "final_break_even", "yearly_break_even"],
    },
    "short_call": {
        "name": "شورت کال",
        "profit_status": "limited_profit",
        "risk_levels": ["high_risk"],
        "sequence": SHORT_CALL_SEQ,
        "desc": SHORT_CALL_DESC,
        "drop_cols": ["end_date", "final_profit", "monthly_profit", "yearly_profit"],
    },
    #
    #
    "long_put": {
        "name": "لانگ پوت",
        "profit_status": "unlimited_profit",
        "risk_levels": ["high_risk"],
        "sequence": LONG_PUT_SEQ,
        "desc": LONG_PUT_DESC,
        "drop_cols": [],
    },
    "short_put": {
        "name": "شورت پوت",
        "profit_status": "limited_profit",
        "risk_levels": ["high_risk"],
        "sequence": SHORT_PUT_SEQ,
        "desc": SHORT_PUT_DESC,
        "drop_cols": ["end_date", "final_profit", "monthly_profit", "yearly_profit"],
    },
    #
    #
    "long_straddle": {
        "name": "لانگ استرادل",
        "profit_status": "unlimited_profit",
        "risk_levels": ["high_risk"],
        "sequence": LONG_STRADDLE_SEQ,
        "desc": LONG_STRADDLE_DESC,
        "drop_cols": ["end_date"],
    },
    "short_straddle": {
        "name": "شورت استرادل",
        "profit_status": "limited_profit",
        "risk_levels": ["high_risk"],
        "sequence": SHORT_STRADDLE_SEQ,
        "desc": SHORT_STRADDLE_DESC,
        "drop_cols": ["end_date", "final_profit", "monthly_profit", "yearly_profit"],
    },
    #
    #
    "bull_call_spread": {
        "name": "بول کال اسپرد",
        "profit_status": "limited_profit",
        "risk_levels": ["low_risk", "high_risk"],
        "sequence": BULL_CALL_SPREAD_SEQ,
        "desc": BULL_CALL_SPREAD_DESC,
        "drop_cols": ["end_date", "final_profit", "yearly_profit"],
    },
    "bear_call_spread": {
        "name": "بیر کال اسپرد",
        "profit_status": "limited_profit",
        "risk_levels": ["high_risk"],
        "sequence": BEAR_CALL_SPREAD_SEQ,
        "desc": BEAR_CALL_SPREAD_DESC,
        "drop_cols": ["end_date", "final_profit", "monthly_profit", "yearly_profit"],
    },
    #
    #
    "bull_put_spread": {
        "name": "بول پوت اسپرد",
        "profit_status": "limited_profit",
        "risk_levels": ["low_risk", "high_risk"],
        "sequence": BULL_PUT_SPREAD_SEQ,
        "desc": BULL_PUT_SPREAD_DESC,
        "drop_cols": ["end_date", "final_profit", "yearly_profit"],
    },
    "bear_put_spread": {
        "name": "بیر پوت اسپرد",
        "profit_status": "limited_profit",
        "risk_levels": ["low_risk", "high_risk"],
        "sequence": BEAR_PUT_SPREAD_SEQ,
        "desc": BEAR_PUT_SPREAD_DESC,
        "drop_cols": ["end_date", "final_profit", "monthly_profit", "yearly_profit"],
    },
    #
    #
    "long_strangle": {
        "name": "لانگ استرانگل",
        "profit_status": "unlimited_profit",
        "risk_levels": ["low_risk", "high_risk"],
        "sequence": LONG_STRANGLE_SEQ,
        "desc": LONG_STRANGLE_DESC,
        "drop_cols": [],
    },
    "short_strangle": {
        "name": "شورت استرانگل",
        "profit_status": "limited_profit",
        "risk_levels": ["high_risk"],
        "sequence": SHORT_STRANGLE_SEQ,
        "desc": SHORT_STRANGLE_DESC,
        "drop_cols": ["end_date", "final_profit", "monthly_profit", "yearly_profit"],
    },
    #
    #
    "long_butterfly": {
        "name": "لانگ باترفلای",
        "profit_status": "limited_profit",
        "risk_levels": ["high_risk"],
        "sequence": LONG_BUTTERFLY_SEQ,
        "desc": LONG_BUTTERFLY_DESC,
        "drop_cols": [
            "end_date",
            "final_profit",
            "yearly_profit",
            "call_buy_value_low",
            "call_sell_value_mid",
            "call_buy_value_high",
        ],
    },
    "short_butterfly": {
        "name": "شورت باترفلای",
        "profit_status": "limited_profit",
        "risk_levels": ["high_risk"],
        "sequence": SHORT_BUTTERFLY_SEQ,
        "desc": SHORT_BUTTERFLY_DESC,
        "drop_cols": [
            "end_date",
            "final_profit",
            "monthly_profit",
            "yearly_profit",
            "call_sell_value_low",
            "call_buy_value_mid",
            "call_sell_value_high",
        ],
    },
    #
    #
    "collar": {
        "name": "کولار",
        "profit_status": "limited_profit",
        "risk_levels": ["low_risk", "high_risk"],
        "sequence": COLLAR_SEQ,
        "desc": COLLAR_DESC,
        "drop_cols": ["end_date", "call_sell_value_low", "call_buy_value_low"],
    },
}


def create_or_update(
    strategy_key: str,
    profit_status: str,
    risk_level: str,
    name: str,
    sequence: int,
    desc: str,
):
    try:
        strategy = StrategyOption.objects.get(
            key=strategy_key, profit_status=profit_status, risk_level=risk_level
        )
        strategy.name = name
        strategy.sequence = sequence
        strategy.desc = desc
        strategy.save()
    except StrategyOption.DoesNotExist:
        strategy = StrategyOption.objects.create(
            name=name,
            key=strategy_key,
            profit_status=profit_status,
            risk_level=risk_level,
            sequence=sequence,
            desc=desc,
        )


def populate_strategy_option():
    print("Creating pre-defined strategies ...")
    for strategy_key, strategy_properties in STRATEGIES.items():
        name = strategy_properties.get("name")
        profit_status = strategy_properties.get("profit_status")
        risk_levels = strategy_properties.get("risk_levels")
        sequence = strategy_properties.get("sequence")
        desc = strategy_properties.get("desc")
        for risk_level in risk_levels:
            create_or_update(
                strategy_key, profit_status, risk_level, name, sequence, desc
            )

    print("Created strategies.")
