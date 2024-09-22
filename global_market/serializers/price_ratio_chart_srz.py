from rest_framework import serializers
from core.serializers import RoundedFloatField


class PriceRatioChartSerailizer(serializers.Serializer):
    trade_date = serializers.DateField()
    avg_price = RoundedFloatField()
