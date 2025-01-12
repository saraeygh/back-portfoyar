from core.configs import (
    OPTION_TRADE_FEE,
    OPTION_SETTLEMENT_FEE,
    BASE_EQUITY_BUY_FEE,
    BASE_EQUITY_SELL_FEE,
)


def edit_last_update(last_update):
    if len(last_update) != 6:
        last_update = "0" + last_update
    last_update = f"{last_update[0:2]}:{last_update[2:4]}:{last_update[4:]}"

    return last_update


def add_details(row, column_mapping: dict):
    result_dict = {}
    for action_key, row_column in column_mapping.items():
        if action_key == "last_update":
            last_update = str(int(row.get(row_column)))
            last_update = edit_last_update(last_update)
            result_dict[action_key] = last_update
        elif action_key == "symbol":
            symbol = str(row.get(row_column))
            name = str(row.get(row_column.replace("symbol", "name")))
            result_dict[action_key] = f"{symbol} - {name}"
        else:
            result_dict[action_key] = row.get(row_column)

    return result_dict


BUY = "buy"
SELL = "sell"

CALL = "call"
PUT = "put"


def get_option_with_fee(strike, premium, action, option_type):
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


def get_base_equity_with_fee(base_equity_price, action: str = BUY):
    if action == BUY:
        base_equity_price = (1 + BASE_EQUITY_BUY_FEE) * base_equity_price
    elif action == SELL:
        base_equity_price = (1 - BASE_EQUITY_SELL_FEE) * base_equity_price
    else:
        return base_equity_price

    return base_equity_price
