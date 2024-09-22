from global_market.models import GlobalCommodityType
from rest_framework import serializers


class GetGlobalCommodityTypeSerailizer(serializers.ModelSerializer):
    class Meta:
        model = GlobalCommodityType
        fields = ["id", "name"]
