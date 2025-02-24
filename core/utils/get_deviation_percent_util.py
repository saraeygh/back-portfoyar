def get_deviation_percent(new_value, old_value):
    try:
        deviation = ((new_value - old_value) / abs(old_value)) * 100
    except ZeroDivisionError:
        deviation = 0

    return deviation
