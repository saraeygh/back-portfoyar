from option_market.models import StrategyOption
from colorama import Fore, Style

COVERED_CALL_SEQ = 1
COVERED_CALL_DESC = "خرید سهم و فروش آپشن خرید همان سهم"

CONVERSION_SEQ = 2
CONVERSION_DESC = (
    "خرید سهم و فروش آپشن خرید و خرید آپشن فروش با قیمت اعمال یکسان همان سهم"
)

LONG_CALL_SEQ = 3
LONG_CALL_DESC = "خرید آپشن خرید"

SHORT_CALL_SEQ = 4
SHORT_CALL_DESC = "فروش آپشن خرید"

LONG_PUT_SEQ = 5
LONG_PUT_DESC = "خرید آپشن فروش"

SHORT_PUT_SEQ = 6
SHORT_PUT_DESC = "فروش آپشن فروش"

LONG_STRADDLE_SEQ = 7
LONG_STRADDLE_DESC = (
    "خرید همزمان آپشن خرید و آپشن فروش با قیمت اعمال برابر مربوط به یک سهم"
)

SHORT_STRADDLE_SEQ = 8
SHORT_STRADDLE_DESC = (
    "فروش همزمان آپشن خرید و آپشن فروش با قیمت اعمال برابر مربوط به یک سهم"
)

BULL_CALL_SPREAD_SEQ = 9
BULL_CALL_SPREAD_DESC = "خرید آپشن خرید با قیمت اعمال پایین‌تر و فروش آپشن خرید با قیمت اعمال بالاتر مربوط به یک سهم"

BEAR_CALL_SPREAD_SEQ = 10
BEAR_CALL_SPREAD_DESC = "خرید آپشن خرید با قیمت اعمال بالاتر و فروش آپشن خرید با قیمت اعمال بالاتر مربوط به یک سهم"

BULL_PUT_SPREAD_SEQ = 11
BULL_PUT_SPREAD_DESC = "خرید آپشن فروش با قیمت اعمال پایین‌تر و فروش آپشن فروش با قیمت اعمال بالاتر مربوط به یک سهم"

BEAR_PUT_SPREAD_SEQ = 12
BEAR_PUT_SPREAD_DESC = "خرید آپشن فروش با قیمت اعمال بالاتر و فروش آپشن فروش با قیمت اعمال پایین‌تر مربوط به یک سهم"

LONG_STRANGLE_SEQ = 13
LONG_STRANGLE_DESC = "خرید آپشن فروش با قیمت اعمال پایین‌تر و خرید آپشن خرید با قیمت اعمال بالاتر مربوط به یک سهم"

SHORT_STRANGLE_SEQ = 14
SHORT_STRANGLE_DESC = "فروش آپشن فروش با قیمت اعمال پایین‌تر و فروش آپشن خرید با قیمت اعمال بالاتر مربوط به یک سهم"

LONG_BUTTERFLY_SEQ = 15
LONG_BUTTERFLY_DESC = "خرید آپشن خرید با قیمت اعمال پایین‌ و دو بار فروش آپشن خرید با قیمت اعمال میانه و خرید آپشن خرید با قیمت اعمال بالای مربوط به یک سهم"

SHORT_BUTTERFLY_SEQ = 16
SHORT_BUTTERFLY_DESC = "فروش آپشن خرید با قیمت اعمال پایین‌ و دو بار خرید آپشن خرید با قیمت اعمال میانه و فروش آپشن خرید با قیمت اعمال بالای مربوط به یک سهم"

COLLAR_SEQ = 17
COLLAR_DESC = "فروش آپشن خرید با قیمت اعمال پایین‌تر و دو بار خرید آپشن خرید با قیمت اعمال بالاتر مربوط به یک سهم"

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
        "profit_status": "unlimited_profit",
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
    print(Fore.BLUE + "Creating pre-defined strategies ..." + Style.RESET_ALL)
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

    print(Fore.GREEN + "Created strategies." + Style.RESET_ALL)
