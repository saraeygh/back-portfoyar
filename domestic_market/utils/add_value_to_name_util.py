def add_value_to_name(row):
    name = row.get("name")
    value = row.get("year_value")
    value = round(value, 3)

    return f"{name} ({value} همت)"
