from rest_framework import serializers
from core.serializers import RoundedFloatField

from stock_market.models.recommendation_config_model import RELATED_NAMES_V2


class StockRecommendedSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    link = serializers.CharField()
    symbol = serializers.CharField()
    total_score = RoundedFloatField()

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        for name in RELATED_NAMES_V2:
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

        for name in RELATED_NAMES_V2:
            if name in instance:
                representation[name] = round(instance[name], 3)

        return representation
