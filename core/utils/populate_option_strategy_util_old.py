from option_market.models import Strategy


def populate_option_strategy_old():
    strategies = {"long_calls": "لانگ کال", "covered_calls": "کاورد کال"}

    print("Creating pre-defined strategies ...")
    for key, name in strategies.items():
        if not Strategy.objects.filter(collection_key=key).exists():
            Strategy.objects.create(name=name, collection_key=key)
    print("Created strategies.")
