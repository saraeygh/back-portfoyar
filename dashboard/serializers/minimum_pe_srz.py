from rest_framework import serializers
from core.serializers import RoundedFloatField


class MinimumPESerailizer(serializers.Serializer):
    symbol = serializers.CharField()
    link = serializers.CharField()
    pe = RoundedFloatField(decimal_places=2)
    sector_pe = RoundedFloatField(decimal_places=2)
    market_cap = serializers.IntegerField()
