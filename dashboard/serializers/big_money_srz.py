from rest_framework import serializers
from core.serializers import RoundedFloatField


class BigMoneySerailizer(serializers.Serializer):
    symbol = serializers.CharField()
    name = serializers.CharField()
    value_mean = RoundedFloatField()
    count_diff = serializers.IntegerField()
    side = serializers.CharField()
    time = serializers.CharField()

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        value_mean = instance.get("value_mean", 0)
        if value_mean < 1:
            representation["value_mean"] = round(value_mean * 100)
            representation["unit"] = "میلیون"
        else:
            representation["unit"] = "میلیارد"

        return representation
