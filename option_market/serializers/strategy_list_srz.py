from rest_framework import serializers
from option_market.models import OptionStrategy, RiskLevel


class RiskLevelListSerializer(serializers.ModelSerializer):
    key = serializers.CharField(source="level")

    class Meta:
        model = RiskLevel
        fields = ("name", "key")


class StrategyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionStrategy
        fields = ("name", "key")
