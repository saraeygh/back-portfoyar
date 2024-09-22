from rest_framework import serializers
from core.serializers import RoundedFloatField


class PersonMoneyFlowSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    link = serializers.CharField()
    symbol = serializers.CharField()
    last_time = serializers.CharField()
    money_flow = RoundedFloatField()
    trade_count = serializers.IntegerField()
    volume = RoundedFloatField()
    value = RoundedFloatField()
    # name = serializers.CharField()
    closing_price = RoundedFloatField()
    closing_price_change = RoundedFloatField(decimal_places=2)
    last_price = RoundedFloatField()
    last_price_change = RoundedFloatField(decimal_places=2)

    history = serializers.ListField(
        child=serializers.DictField(
            style={"type": "object"}, required=False, default={}
        )
    )

    def to_representation(self, instance):
        not_rounded_history = instance.pop("history")
        rounded_history = []
        for point in not_rounded_history:
            point["value"] = round(point.pop("value"), 3)
            rounded_history.append(point)

        instance["history"] = rounded_history
        instance["symbol"] = f"{instance["symbol"]} ({instance["name"]})"

        return super().to_representation(instance)



class PersonBuyPressureSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    link = serializers.CharField()
    symbol = serializers.CharField()
    last_time = serializers.CharField()
    buy_pressure = RoundedFloatField(decimal_places=1)
    trade_count = serializers.IntegerField()
    volume = RoundedFloatField()
    value = RoundedFloatField()
    # name = serializers.CharField()
    closing_price = RoundedFloatField()
    closing_price_change = RoundedFloatField(decimal_places=2)
    last_price = RoundedFloatField()
    last_price_change = RoundedFloatField(decimal_places=2)

    history = serializers.ListField(
        child=serializers.DictField(
            style={"type": "object"}, required=False, default={}
        )
    )

    def to_representation(self, instance):
        not_rounded_history = instance.pop("history")
        rounded_history = []
        for point in not_rounded_history:
            point["value"] = round(point.pop("value"), 3)
            rounded_history.append(point)

        instance["history"] = rounded_history

        instance["symbol"] = f"{instance["symbol"]} ({instance["name"]})"

        return super().to_representation(instance)


class PersonBuyValueSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    link = serializers.CharField()
    symbol = serializers.CharField()
    last_time = serializers.CharField()
    buy_value = RoundedFloatField()
    trade_count = serializers.IntegerField()
    volume = RoundedFloatField()
    value = RoundedFloatField()
    # name = serializers.CharField()
    closing_price = RoundedFloatField()
    closing_price_change = RoundedFloatField(decimal_places=2)
    last_price = RoundedFloatField()
    last_price_change = RoundedFloatField(decimal_places=2)

    history = serializers.ListField(
        child=serializers.DictField(
            style={"type": "object"}, required=False, default={}
        )
    )

    def to_representation(self, instance):
        not_rounded_history = instance.pop("history")
        rounded_history = []
        for point in not_rounded_history:
            point["value"] = round(point.pop("value"), 3)
            rounded_history.append(point)

        instance["history"] = rounded_history
        instance["symbol"] = f"{instance["symbol"]} ({instance["name"]})"

        return super().to_representation(instance)


class BuyOrderRatioSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    link = serializers.CharField()
    symbol = serializers.CharField()
    last_time = serializers.CharField()
    buy_ratio = RoundedFloatField(decimal_places=0)
    trade_count = serializers.IntegerField()
    volume = RoundedFloatField()
    value = RoundedFloatField()
    # name = serializers.CharField()
    closing_price = RoundedFloatField()
    closing_price_change = RoundedFloatField(decimal_places=2)
    last_price = RoundedFloatField()
    last_price_change = RoundedFloatField(decimal_places=2)

    history = serializers.ListField(
        child=serializers.DictField(
            style={"type": "object"}, required=False, default={}
        )
    )

    def to_representation(self, instance):
        not_rounded_history = instance.pop("history")
        rounded_history = []
        for point in not_rounded_history:
            point["value"] = round(point.pop("value"), 3)
            rounded_history.append(point)

        instance["history"] = rounded_history
        instance["symbol"] = f"{instance["symbol"]} ({instance["name"]})"

        return super().to_representation(instance)



class SellOrderRatioSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    link = serializers.CharField()
    symbol = serializers.CharField()
    last_time = serializers.CharField()
    sell_ratio = RoundedFloatField(decimal_places=0)
    trade_count = serializers.IntegerField()
    volume = RoundedFloatField()
    value = RoundedFloatField()
    # name = serializers.CharField()
    closing_price = RoundedFloatField()
    closing_price_change = RoundedFloatField(decimal_places=2)
    last_price = RoundedFloatField()
    last_price_change = RoundedFloatField(decimal_places=2)

    history = serializers.ListField(
        child=serializers.DictField(
            style={"type": "object"}, required=False, default={}
        )
    )

    def to_representation(self, instance):
        not_rounded_history = instance.pop("history")
        rounded_history = []
        for point in not_rounded_history:
            point["value"] = round(point.pop("value"), 3)
            rounded_history.append(point)

        instance["history"] = rounded_history
        instance["symbol"] = f"{instance["symbol"]} ({instance["name"]})"

        return super().to_representation(instance)
