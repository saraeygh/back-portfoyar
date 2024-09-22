from rest_framework import serializers
from core.serializers import RoundedFloatField


class StockValueChangeSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    link = serializers.CharField()
    symbol = serializers.CharField()
    last_update = serializers.CharField()
    mean = RoundedFloatField(decimal_places=2)
    value = RoundedFloatField(decimal_places=2)
    value_change = RoundedFloatField(decimal_places=1)
    # name = serializers.CharField()
    trade_count = serializers.IntegerField()
    volume = RoundedFloatField(decimal_places=2)
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
