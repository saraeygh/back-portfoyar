from core.configs import (
    OPTION_TRADE_FEE,
    OPTION_SETTLEMENT_FEE,
    BASE_EQUITY_BUY_FEE,
    BASE_EQUITY_SELL_FEE,
)

BUY = "buy"
SELL = "sell"

CALL = "call"
PUT = "put"


def add_option_fee(strike, premium, action, option_type):
    if action == BUY and option_type == CALL:
        strike = (1 + OPTION_SETTLEMENT_FEE) * strike
        premium = (1 + OPTION_TRADE_FEE) * premium
    elif action == SELL and option_type == CALL:
        strike = (1 - OPTION_SETTLEMENT_FEE) * strike
        premium = (1 - OPTION_TRADE_FEE) * premium
    elif action == BUY and option_type == PUT:
        strike = (1 - OPTION_SETTLEMENT_FEE) * strike
        premium = (1 + OPTION_TRADE_FEE) * premium
    elif action == SELL and option_type == PUT:
        strike = (1 + OPTION_SETTLEMENT_FEE) * strike
        premium = (1 - OPTION_TRADE_FEE) * premium
    else:
        return strike, premium

    return strike, premium


def add_base_equity_fee(base_equity_price, action: str = BUY):
    if action == BUY:
        base_equity_price = (1 + BASE_EQUITY_BUY_FEE) * base_equity_price
    elif action == SELL:
        base_equity_price = (1 - BASE_EQUITY_SELL_FEE) * base_equity_price
    else:
        return base_equity_price

    return base_equity_price


def get_profits(profits, numerator, denominator, remained_day):

    if denominator != 0:
        profits["final_profit"] = (numerator / denominator) * 100

    if remained_day != 0:
        profits["monthly_profit"] = (profits["final_profit"] / remained_day) * 30

    profits["yearly_profit"] = profits["monthly_profit"] * 12

    return profits


def get_base_equity_fee(base_equity):
    base_equity_action, base_equity_price = base_equity[0], base_equity[1]
    if base_equity_action == BUY:
        base_equity_fee = base_equity_price * BASE_EQUITY_BUY_FEE
    else:
        base_equity_fee = base_equity_price * BASE_EQUITY_SELL_FEE

    return base_equity_fee


def get_fee_percent(
    results,
    strike_sum=0,
    premium_sum=0,
    base_equity=[BUY, 0],
    net_pay=1,
):
    strike_fee = strike_sum * OPTION_SETTLEMENT_FEE
    premium_fee = premium_sum * OPTION_TRADE_FEE
    base_equity_fee = get_base_equity_fee(base_equity)

    results["fee"] = (sum([strike_fee, premium_fee, base_equity_fee]) / net_pay) * 100

    return results
