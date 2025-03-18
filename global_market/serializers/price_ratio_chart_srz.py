import jdatetime

from rest_framework import serializers
from core.serializers import RoundedFloatField


class PriceChartSerializer(serializers.Serializer):
    trade_date = serializers.DateField()
    avg_price = RoundedFloatField()

    def to_representation(self, instance):
        instance["trade_date"] = jdatetime.date.fromgregorian(
            date=instance["trade_date"], locale="fa_IR"
        )
        representation = super().to_representation(instance)
        return representation


class RatioChartSerializer(serializers.Serializer):
    trade_date = serializers.DateField()
    avg_price = RoundedFloatField()
    mean = RoundedFloatField()

    def to_representation(self, instance):
        instance["trade_date"] = jdatetime.date.fromgregorian(
            date=instance["trade_date"], locale="fa_IR"
        )
        representation = super().to_representation(instance)
        return representation
