def get_deviation_percent(new_value, old_value, diff_value: int = 0):
    try:
        deviation = (((new_value - old_value) - diff_value) / abs(old_value)) * 100
    except ZeroDivisionError:
        deviation = 0

    return deviation
