from rest_framework import serializers
from core.serializers import RoundedFloatField


RELATED_NAMES = [
    "money_flow",
    "buy_pressure",
    "buy_value",
    "buy_ratio",
    "sell_ratio",
    "roi",
    "value_change",
    "call_value_change",
    "put_value_change",
    "option_price_spread",
    "global_positive_range",
    "global_negative_range",
    "domestic_positive_range",
    "domestic_negative_range",
]


class StockRecommendedSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    link = serializers.CharField()
    symbol = serializers.CharField()
    total_score = RoundedFloatField()

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        for name in RELATED_NAMES:
            if name in instance:
                score = f"{name}_score"
                representation[name] = round(instance[name], 3)
                representation[score] = round(instance[score], 3)

        return representation


class SummaryStockRecommendedSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    link = serializers.CharField()
    symbol = serializers.CharField()
    total_score = RoundedFloatField()

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        for name in RELATED_NAMES:
            if name in instance:
                representation[name] = round(instance[name], 3)

        return representation
