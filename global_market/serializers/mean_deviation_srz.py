from rest_framework import serializers
from core.serializers import RoundedFloatField


class GlobalMeanDeviationSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    commodity = serializers.CharField()
    commodity_type = serializers.CharField()
    industry = serializers.CharField()
    transit = serializers.CharField()
    global_mean = RoundedFloatField()
    global_last_price = RoundedFloatField()
    deviation = RoundedFloatField(decimal_places=2)
    last_price_date = serializers.CharField()
    chart = serializers.DictField()


class SummaryGlobalMeanDeviationSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    commodity = serializers.CharField()
    commodity_type = serializers.CharField()
    transit = serializers.CharField()
    global_mean = RoundedFloatField()
    global_last_price = RoundedFloatField()
    deviation = RoundedFloatField(decimal_places=2)
    last_price_date = serializers.CharField()
    chart = serializers.DictField()


class DashboardGlobalMeanDeviationSerailizer(serializers.Serializer):
    commodity_type = serializers.CharField()
    transit = serializers.CharField()
    deviation = RoundedFloatField(decimal_places=2)
    last_price_date = serializers.CharField()
