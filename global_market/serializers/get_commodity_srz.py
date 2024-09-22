from global_market.models import GlobalCommodity
from rest_framework import serializers


class GetGlobalCommoditySerailizer(serializers.ModelSerializer):
    class Meta:
        model = GlobalCommodity
        fields = ["id", "name"]
