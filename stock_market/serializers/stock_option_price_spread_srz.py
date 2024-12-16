from rest_framework import serializers
from core.serializers import RoundedFloatField


class StockOptionPriceSpreadSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    links = serializers.ListField()
    asset_name = serializers.CharField()
    base_equit_price = serializers.IntegerField()

    symbol = serializers.CharField()
    strike = serializers.IntegerField()
    premium = serializers.IntegerField()
    price_spread = RoundedFloatField(decimal_places=2)
    days_to_expire = serializers.IntegerField()
    last_update = serializers.CharField()
    expiration_date = serializers.CharField()
    value = RoundedFloatField(decimal_places=0)
    strike_premium = RoundedFloatField()
    chart = serializers.DictField()

    def to_representation(self, instance):
        instance["links"] = [
            {"name": "لینک تابلوی معاملات اختیار", "link": instance.get("option_link")},
            {"name": "لینک تابلوی معاملات سهام", "link": instance.get("stock_link")},
        ]
        return super().to_representation(instance)


class SummaryStockOptionPriceSpreadSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    links = serializers.ListField()
    asset_name = serializers.CharField()
    base_equit_price = serializers.IntegerField()

    symbol = serializers.CharField()
    strike = serializers.IntegerField()
    premium = serializers.IntegerField()
    price_spread = RoundedFloatField(decimal_places=2)
    days_to_expire = serializers.IntegerField()
    value = RoundedFloatField(decimal_places=0)

    def to_representation(self, instance):
        instance["links"] = [
            {"name": "لینک تابلوی معاملات اختیار", "link": instance.get("option_link")},
            {"name": "لینک تابلوی معاملات سهام", "link": instance.get("stock_link")},
        ]
        return super().to_representation(instance)


class StockOptionPriceSpreadDashboardSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    links = serializers.ListField()
    asset_name = serializers.CharField()
    base_equit_price = serializers.IntegerField()

    symbol = serializers.CharField()
    strike = serializers.IntegerField()
    premium = serializers.IntegerField()
    price_spread = RoundedFloatField(decimal_places=2)
    days_to_expire = serializers.IntegerField()
    last_time = serializers.CharField(source="last_update")
    expiration_date = serializers.CharField()
    value = RoundedFloatField(decimal_places=0)
    strike_premium = RoundedFloatField()
    last_price = RoundedFloatField()
    last_price_change = RoundedFloatField(decimal_places=2)
    chart = serializers.DictField()

    def to_representation(self, instance):
        instance["links"] = [
            {"name": "لینک تابلوی معاملات اختیار", "link": instance.get("option_link")},
            {"name": "لینک تابلوی معاملات سهام", "link": instance.get("stock_link")},
        ]
        return super().to_representation(instance)
