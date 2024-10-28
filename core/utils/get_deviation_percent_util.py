def get_deviation_percent(new_value, old_value):

    deviation = ((new_value - old_value) / abs(old_value)) * 100

    return deviation
