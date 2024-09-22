from rest_framework import serializers


class StockFavoriteInstrumentListSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    symbol = serializers.CharField()
    name = serializers.CharField()

    def to_representation(self, instance: dict):
        symbol = instance.pop("symbol")
        name = instance.pop("name")
        instance["name"] = f"{name} ({symbol})"

        return instance
