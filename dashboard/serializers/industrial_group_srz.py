from rest_framework import serializers

from stock_market.models import StockIndustrialGroup


class IndustrialGroupSerailizer(serializers.ModelSerializer):

    class Meta:
        model = StockIndustrialGroup
        fields = ["code", "name"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["id"] = representation.pop("code")

        return representation
