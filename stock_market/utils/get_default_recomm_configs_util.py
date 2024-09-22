ASCENDING_WEIGHT_THRESHOLD_INDICES = [
    "money_flow",
    "buy_pressure",
    "buy_value",
    "buy_ratio",
    "sell_ratio",
    "value_change",
    "call_value_change",
    "put_value_change",
    "option_price_spread",
]

ASCENDING_WEIGHT_THRESHOLD_DURATION_INDICES = [
    "roi",
    "global_positive_range",
    "global_negative_range",
]

ASCENDING_WEIGHT_THRESHOLD_DURATION_COMMODITY_RATIO_INDICES = [
    "domestic_positive_range",
    "domestic_negative_range",
]


def get_default_recomm_configs(related_objects):
    config = []

    for obj_name, obj in related_objects.items():
        if obj_name in ASCENDING_WEIGHT_THRESHOLD_INDICES:
            if obj.is_enabled:
                new_index = {
                    "name": obj_name,
                    "weight": obj.weight,
                    "threshold_value": obj.threshold_value,
                }
                config.append(new_index)

        elif obj_name in ASCENDING_WEIGHT_THRESHOLD_DURATION_INDICES:
            if obj.is_enabled:
                new_index = {
                    "name": obj_name,
                    "weight": obj.weight,
                    "threshold_value": obj.threshold_value,
                    "duration": obj.duration,
                }
                config.append(new_index)

        elif obj_name in ASCENDING_WEIGHT_THRESHOLD_DURATION_COMMODITY_RATIO_INDICES:
            if obj.is_enabled:
                new_index = {
                    "name": obj_name,
                    "weight": obj.weight,
                    "threshold_value": obj.threshold_value,
                    "duration": obj.duration,
                    "min_commodity_ratio": obj.min_commodity_ratio,
                }
                config.append(new_index)

        else:
            continue

    return config
