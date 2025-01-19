import uuid

from rest_framework import serializers

from core.serializers import RoundedFloatField
from core.configs import RIAL_TO_BILLION_TOMAN


class SymbolHistorySerializer(serializers.Serializer):
    id = serializers.UUIDField(default=uuid.uuid4, read_only=True)
    date = serializers.CharField()
    symbol = serializers.CharField()
    asset_name = serializers.CharField()
    equit_close_price = serializers.IntegerField()
    strike = serializers.IntegerField()
    expiration_date = serializers.CharField()

    quantity = RoundedFloatField()
    volume = RoundedFloatField()
    value = RoundedFloatField()

    yesterday_price = RoundedFloatField()
    first_price = RoundedFloatField()
    last_trade = RoundedFloatField()
    price_min = RoundedFloatField()
    price_max = RoundedFloatField()
    close_price = RoundedFloatField()
    premium_strike = serializers.SerializerMethodField()

    def get_premium_strike(self, instance):
        premium_strike = instance["strike"] + instance["close_price"]
        return premium_strike

    def to_representation(self, instance):
        instance["value"] = instance["value"] / RIAL_TO_BILLION_TOMAN
        representation = super().to_representation(instance)
        return representation
