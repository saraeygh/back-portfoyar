from rest_framework import serializers
from core.serializers import RoundedFloatField


class StockOptionValueChangeSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    link = serializers.CharField()
    symbol = serializers.CharField()
    last_update = serializers.CharField()
    month_mean = RoundedFloatField(decimal_places=2)
    last_mean = RoundedFloatField(decimal_places=2)
    value_change = RoundedFloatField(decimal_places=1)
    daily_roi = RoundedFloatField(decimal_places=2)
    pe = RoundedFloatField()
    sector_pe = RoundedFloatField()
    ps = RoundedFloatField()
    market_cap = RoundedFloatField(decimal_places=0)
