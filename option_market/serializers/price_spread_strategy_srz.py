from rest_framework import serializers
from core.serializers import RoundedFloatField


class PriceSpreadStrategySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    option_link = serializers.CharField()
    stock_link = serializers.CharField()

    asset_name = serializers.CharField()
    base_equit_price = serializers.IntegerField()

    symbol = serializers.CharField()
    premium = serializers.IntegerField()

    strike_premium = serializers.IntegerField()

    price_spread = RoundedFloatField()
    days_to_expire = serializers.IntegerField()
    monthly_price_spread = RoundedFloatField()

    value = RoundedFloatField(decimal_places=1)

    def to_representation(self, instance):
        instance["symbol"] = f"{instance.pop("symbol")} - {instance.pop("strike")}"

        return super().to_representation(instance)
