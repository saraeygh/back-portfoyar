from core.configs import (
    OPTION_TRADE_FEE,
    OPTION_PHYSICAL_SETTLEMENT_FEE,
    OPTION_LIQUIDATION_SETTLEMENT_FEE,
)


def edit_last_update(last_update):
    if len(last_update) != 6:
        last_update = "0" + last_update
    last_update = f"{last_update[0:2]}:{last_update[2:4]}:{last_update[4:]}"

    return last_update


def add_action_detail(row, column_mapping: dict):
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


def add_option_fees(row):

    cs = float(row.get("contract_size"))
    strike = float(row.get("strike_price"))

    trade_fee = OPTION_TRADE_FEE * strike
    liquidation_settlement_fee = strike * cs * OPTION_LIQUIDATION_SETTLEMENT_FEE
    physical_settlement_fee = strike * cs * OPTION_PHYSICAL_SETTLEMENT_FEE

    fees = {
        "trade_fee": round(trade_fee, 2),
        "liquidation_settlement_fee": round(liquidation_settlement_fee, 2),
        "physical_settlement_fee": round(physical_settlement_fee, 2),
        "total_fee": round(
            trade_fee + liquidation_settlement_fee + physical_settlement_fee, 2
        ),
    }

    return fees
