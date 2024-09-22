from rest_framework import serializers
from core.serializers import RoundedFloatField


class StockOptionPriceSpreadSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    option_link = serializers.CharField()
    stock_link = serializers.CharField()
    symbol = serializers.CharField()
    strike = serializers.IntegerField()
    asset_name = serializers.CharField()
    base_equit_price = serializers.IntegerField()
    price_spread = RoundedFloatField(decimal_places=2)
    days_to_expire = serializers.IntegerField()
    last_update = serializers.CharField()
    expiration_date = serializers.CharField()
    option_type = serializers.CharField()
    value = RoundedFloatField(decimal_places=0)
    strike_premium = RoundedFloatField()
