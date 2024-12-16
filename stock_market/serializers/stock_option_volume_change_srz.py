from rest_framework import serializers
from core.serializers import RoundedFloatField


class StockOptionValueChangeSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    links = serializers.ListField()
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
    chart = serializers.DictField()

    def to_representation(self, instance):
        instance["links"] = [
            {"name": "لینک تابلوی معاملات", "link": instance.get("link")}
        ]
        return super().to_representation(instance)


class SummaryStockOptionValueChangeSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    links = serializers.ListField()
    symbol = serializers.CharField()
    month_mean = RoundedFloatField(decimal_places=2)
    last_mean = RoundedFloatField(decimal_places=2)
    value_change = RoundedFloatField(decimal_places=1)
    daily_roi = RoundedFloatField(decimal_places=2)
    market_cap = RoundedFloatField(decimal_places=0)

    def to_representation(self, instance):
        instance["links"] = [
            {"name": "لینک تابلوی معاملات", "link": instance.get("link")}
        ]
        return super().to_representation(instance)


class StockOptionValueChangeDashboardSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    links = serializers.ListField()
    symbol = serializers.CharField()
    last_time = serializers.CharField(source="last_update")
    month_mean = RoundedFloatField(decimal_places=2)
    last_mean = RoundedFloatField(decimal_places=2)
    value_change = RoundedFloatField(decimal_places=1)
    daily_roi = RoundedFloatField(decimal_places=2)
    pe = RoundedFloatField()
    sector_pe = RoundedFloatField()
    ps = RoundedFloatField()
    market_cap = RoundedFloatField(decimal_places=0)
    last_price = RoundedFloatField()
    last_price_change = RoundedFloatField(decimal_places=2)
    chart = serializers.DictField()

    def to_representation(self, instance):
        instance["links"] = [
            {"name": "لینک تابلوی معاملات", "link": instance.get("link")}
        ]
        return super().to_representation(instance)
