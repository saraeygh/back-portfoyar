from rest_framework import serializers
from option_market.models import Strategy


class StrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategy
        fields = ("id", "name", "collection_key")
