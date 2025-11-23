def edit_last_update(last_update):
    if len(last_update) != 6:
        last_update = "0" + last_update
    last_update = f"{last_update[0:2]}:{last_update[2:4]}:{last_update[4:]}"

    return last_update


def add_details(row, column_mapping: dict):
    result_dict = {}
    for action_key, row_column in column_mapping.items():
        if action_key == "last_update":
            last_update = str(int(getattr(row, row_column)))
            last_update = edit_last_update(last_update)
            result_dict[action_key] = last_update
        elif action_key == "symbol":
            symbol = str(getattr(row, row_column))
            name = str(getattr(row, row_column)).replace("symbol", "name")
            result_dict[action_key] = f"{symbol} - {name}"
        elif action_key == "order_book":
            result_dict[action_key] = getattr(row, row_column)
        else:
            result_dict[action_key] = int(getattr(row, row_column))

    return result_dict
