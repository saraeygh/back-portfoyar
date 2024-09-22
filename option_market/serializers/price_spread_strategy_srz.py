from rest_framework import serializers

from core.serializers import RoundedFloatField


class PriceSpreadStrategySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    option_link = serializers.CharField()
    stock_link = serializers.CharField()
    symbol = serializers.CharField()
    asset_name = serializers.CharField()

    strike = serializers.IntegerField()
    premium = serializers.IntegerField()
    base_equit_price = serializers.IntegerField()
    strike_premium = serializers.IntegerField()
    price_spread = RoundedFloatField()
    monthly_price_spread = RoundedFloatField()

    expiration_date = serializers.CharField()
    days_to_expire = serializers.IntegerField()

    option_type = serializers.CharField()

    volume = RoundedFloatField(decimal_places=1)
    value = RoundedFloatField(decimal_places=1)
    number = RoundedFloatField(decimal_places=1)

    best_buy_price = serializers.IntegerField()
    best_buy_volume = serializers.IntegerField()

    best_sell_price = serializers.IntegerField()
    best_sell_volume = serializers.IntegerField()
